import random
from typing import Any, Callable, Coroutine, Iterable
from dialoger.handler import Handler, OtherwiseHandler, IntentHandler, TriggerHandler, PromptHandler
from dialoger.reply import Reply, TextReply
from dialoger.input import Input
from dialoger.response_builder import ResponseBuilder
from dialoger.similarity_index import SimilarityIndex, similarity_index


class Dialog:
    _sim_index: SimilarityIndex
    _handlers: list[Handler]
    _replies: list[Reply]
    _generation: int
    _input: Input | None
    _postproc_replies: Callable[[list[Reply]], list[Reply]] | None
    _stopwords: frozenset[str]

    def __init__(self, *, stopwords: Iterable[str] = []) -> None:
        self._handlers = []
        self._sim_index = similarity_index
        self._generation = 0
        self._replies = []
        self._postproc_replies = None
        self._stopwords = frozenset(stopwords)

    # Dialog flow API
    # ---------------

    def append_handler(self,
        *intent: str,
        trigger: Callable[[Input], bool] | None = None,
        yes: bool = False
    ):
        def decorator(action: Callable[[], Coroutine[Any, Any, None]]):
            assert not (trigger and intent), 'Параметры trigger и примеры фраз несовместимы'
            assert not (trigger and yes), 'Параметры trigger и yes несовместимы'

            if len(intent) or yes:
                phrases = intent

                if yes:
                    phrases = phrases + ('да', 'давай', 'хочу', 'буду', 'хорошо', 'согласен')

                self._handlers.append(IntentHandler(
                    phrases=phrases,
                    action=action,
                    generation=self._generation,
                ))

            elif trigger:
                self._handlers.append(TriggerHandler(
                    trigger=trigger,
                    action=action,
                    generation=self._generation,
                ))
            else:
                self._handlers.append(OtherwiseHandler(
                    action=action,
                    generation=self._generation,
                ))

            return action

        return decorator

    def append_reply(self, *replies: Reply | str | tuple[str,str]):
        for reply in replies:
            match reply:
                case Reply():
                    self._replies.append(reply)
                case _:
                    self._replies.append(TextReply(reply))

    def append_prompt(self):
        def decorator(action: Callable[[], Coroutine[Any, Any, None]]):
            self._handlers.append(PromptHandler(
                action=action,
                generation=self._generation,
            ))

            return action

        return decorator

    def input(self) -> Input:
        assert self._input

        return self._input

    def postproc_replies(self, fn: Callable[[list[Reply]], list[Reply]]):
        self._postproc_replies = fn

        return fn

    # Server API
    # ----------

    async def handle_request(self, request: dict) -> dict:
        self._generation += 1
        response_builder = ResponseBuilder()
        input = Input(request)

        if input.is_ping:
            response_builder.append_text("Pong!")
            response_builder.end_session()
        else:
            await self._generate_response(input)

        self._replies_to_response(response_builder)

        return response_builder.build()

    def after_response(self):
        self._input = None
        self._drop_outdated_handlers()
        self._warmup_sim_index()
        self._replies = []

    # Implementation
    # --------------

    def _replies_to_response(self, response_builder: ResponseBuilder):
        if self._postproc_replies:
            self._replies = self._postproc_replies(self._replies)

        for reply in self._replies:
            reply.append_to(response_builder)

    async def _generate_response(self, input: Input) -> None:
        """
        Выбор и выполнение хендлера
        """
        self._input = input

        _ = await self._handle_by_triggers(input) or \
            await self._handle_by_intents(input) or \
            await self._handle_by_otherwise()

        await self._apply_prompts()

        if not self._replies:
            self.append_reply("Я тебя полохо слышу. Подойти ближе.")

    async def _handle_by_triggers(self, input: Input) -> bool:
        for h in reversed(self._handlers):
            if isinstance(h, TriggerHandler) and h.trigger(input):
                await h.action()

                return True

        return False

    async def _handle_by_intents(self, input: Input) -> bool:
        intent_handlers = [h for h in self._handlers if isinstance(h, IntentHandler)]
        without_stopwords = ' '.join(t for t in input.tokens if t not in self._stopwords)

        if not intent_handlers or not without_stopwords:
            return False

        most_similar = self._sim_index.most_similar(
            intents=[h.phrases for h in intent_handlers],
            text=without_stopwords
        )

        if most_similar is None:
            return False

        await intent_handlers[most_similar].action()

        return True

    async def _handle_by_otherwise(self) -> bool:
        for h in reversed(self._handlers):
            if isinstance(h, OtherwiseHandler):
                await h.action()

                return True

        return False

    async def _apply_prompts(self):
        if self._generation % 4 != 0:
            return

        has_new_handlers = next((True for h in self._handlers if h.generation == self._generation), False)

        if has_new_handlers:
            return

        prompts = [h for h in self._handlers if isinstance(h, PromptHandler)]

        if not prompts:
            return

        random.shuffle(prompts)
        prompts.sort(key=lambda h: -h.generation)

        await prompts[0].action()
        self._handlers.remove(prompts[0])

    def _drop_outdated_handlers(self):
        """
        Отбрасывает неактуальные обработчики
        """
        self._handlers = [h for h in self._handlers if h.generation in (0, self._generation)]

    def _warmup_sim_index(self):
        """
        Энкодер может работать достаточно долго
        Так что переносим его работу на фазу после ответа
        """
        for h in self._handlers:
            match h:
                case IntentHandler(phrases=p):
                    self._sim_index.add(p)
