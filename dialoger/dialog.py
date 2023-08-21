from typing import Any, Iterable, cast
from dialoger.handler import (
    Handler,
    OtherwiseHandler,
    IntentHandler,
    TriggerHandler,
)
from dialoger.reply import Reply, TextReply
from dialoger.input import Input
from dialoger.response_builder import DialogResponse, ResponseBuilder
from dialoger.similarity_index import SimilarityIndex, similarity_index


DialogRequest = dict[Any, Any]


class Dialog:
    _sim_index: SimilarityIndex
    _handlers: list[Handler]
    _replies: list[Reply]
    _input: Input | None
    _stopwords: frozenset[str]

    def __init__(self, *, stopwords: Iterable[str] = []) -> None:
        self._handlers = []
        self._sim_index = similarity_index
        self._replies = []
        self._stopwords = frozenset(stopwords)

    # Dialog API
    # ---------------

    def append_handler(self, handler: Handler):
        self._handlers.append(handler)

    def append_reply(self, reply: Reply):
        self._replies.append(reply)

    def input(self) -> Input:
        assert self._input

        return self._input

    # Server API
    # ----------

    async def handle_request(self, request: DialogRequest) -> DialogResponse:
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
        self._update_ttl_and_drop_outdated_handlers()
        self._warmup_sim_index()
        self._replies = []

    # Implementation
    # --------------

    def _replies_to_response(self, response_builder: ResponseBuilder):
        for reply in self._replies:
            reply.append_to(response_builder)

    async def _generate_response(self, input: Input) -> None:
        """
        Выбор и выполнение хендлера
        """
        self._input = input

        _ = (
            await self._handle_by_triggers(input)
            or await self._handle_by_intents(input)
            or await self._handle_by_otherwise()
        )

        await self._apply_postrolls()

        if not self._replies:
            self.append_reply(
                TextReply("Я тебя плохо слышу. Подойти поближе и повтори.")
            )

    async def _handle_by_triggers(self, input: Input) -> bool:
        for h in reversed(self._handlers):
            match h:
                case TriggerHandler(_, action, trigger):
                    result = trigger(input)

                    if result:
                        maybe_coroutine = action(result)

                        if maybe_coroutine is not None:
                            await maybe_coroutine

                        return True
                case _:
                    pass

        return False

    async def _handle_by_intents(self, input: Input) -> bool:
        intent_handlers = [h for h in self._handlers if isinstance(h, IntentHandler)]

        input_without_stopwords = " ".join(
            t for t in input.tokens if t not in self._stopwords
        )

        if not intent_handlers or not input_without_stopwords:
            return False

        most_similar = self._sim_index.most_similar(
            intents=[h.phrases for h in intent_handlers], text=input_without_stopwords
        )

        if most_similar is None:
            return False

        maybe_coroutine = intent_handlers[most_similar].action()

        if maybe_coroutine is not None:
            await maybe_coroutine

        return True

    async def _handle_by_otherwise(self) -> bool:
        for h in reversed(self._handlers):
            if isinstance(h, OtherwiseHandler):
                maybe_coroutine = h.action()

                if maybe_coroutine is not None:
                    await maybe_coroutine

                return True

        return False

    async def _apply_postrolls(self):
        pass
        # if self._generation % 4 != 0:
        #     return

        # has_new_handlers = next(
        #     (True for h in self._handlers if h.time_to_live == self._generation), False
        # )

        # if has_new_handlers:
        #     return

        # postrolls = [h for h in self._handlers if isinstance(h, PostrollHandler)]

        # if not postrolls:
        #     return

        # random.shuffle(postrolls)
        # postrolls.sort(key=lambda h: -h.generation)

        # maybe_coroutine = postrolls[0].action()

        # if maybe_coroutine is not None:
        #     await maybe_coroutine

        # self._handlers.remove(postrolls[0])

    def _update_ttl_and_drop_outdated_handlers(self):
        """
        Отбрасывает неактуальные обработчики
        """
        for h in self._handlers:
            h.time_to_live -= 1

        # У обработчиков на текущем цикле ttl = 1, после вычетания станет 0
        self._handlers = [h for h in self._handlers if h.time_to_live >= 0]

    def _warmup_sim_index(self):
        """
        Энкодер может работать достаточно долго
        Так что переносим его работу на фазу после ответа
        """
        for h in self._handlers:
            match h:
                case IntentHandler(phrases=p):
                    self._sim_index.add(p)
                case _:
                    pass
