from types import FunctionType
from typing import Callable, Iterable
from dialoger.handler import Handler, OtherwiseHandler, PhraseHandler, TriggerHandler
from dialoger.reply import Reply
from dialoger.input import Input
from dialoger.response_builder import ResponseBuilder
from dialoger.similarity_index import SimilarityIndex, similarity_index


class Dialog:
    _sim_index: SimilarityIndex
    _handlers: list[Handler]
    _replies: list[Reply]
    _requests_count: int
    _input: Input | None
    _postproc_replies: Callable[[list[Reply]], list[Reply]] | None
    _stopwords: frozenset[str]

    def __init__(self) -> None:
        self._handlers = []
        self._sim_index = similarity_index
        self._requests_count = 0
        self._replies = []
        self._postproc_replies = None
        self._stopwords = frozenset()

    def handle_request(self, request: dict) -> dict:
        self._requests_count += 1
        response_builder = ResponseBuilder()
        input = Input(request)

        if input.is_ping:
            response_builder.append_text("Pong!")
            response_builder.end_session()
        else:
            self._generate_response(input)

        self._replies_to_response(response_builder)

        return response_builder.build()

    def after_response(self):
        self._input = None
        self._drop_outdated_handlers()
        self._warmup_sim_index()

    def append_handler(self, *intent: str, trigger: Callable[[Input], bool] | None = None):
        def decorator(action: Callable[[], None]):
            if len(intent):
                self._handlers.append(PhraseHandler(
                    phrases=tuple(phrase for phrase in intent if phrase not in self._stopwords),
                    action=action,
                    generation=self._requests_count,
                ))

            elif trigger:
                self._handlers.append(TriggerHandler(
                    trigger=trigger,
                    action=action,
                    generation=self._requests_count,
                ))
            else:
                self._handlers.append(OtherwiseHandler(
                    action=action,
                    generation=self._requests_count,
                ))

            return action

        return decorator

    def append_reply(self, *replies: str | tuple[str,str] | Reply ):
        for reply in replies:
            match reply:
                case Reply():
                    self._replies.append(reply)
                case _:
                    self._replies.append(Reply(reply))

    def input(self) -> Input:
        assert self._input

        return self._input

    def postproc_replies(self, fn: Callable[[list[Reply]], list[Reply]]):
        self._postproc_replies = fn

        return fn

    def _replies_to_response(self, response_builder: ResponseBuilder):
        if self._postproc_replies:
            self._replies = self._postproc_replies(self._replies)

        for reply in self._replies:
            reply.append_to(response_builder)

    def _generate_response(self, input: Input) -> None:
        """
        Выбор и выполнение хендлера
        """
        self._input = input
        self._replies = []

        triggered = next((h for h in self._handlers if isinstance(h, TriggerHandler) and h.trigger(input)), None)

        if triggered:
            triggered.action()

            return

        phrased = [h for h in self._handlers if isinstance(h, PhraseHandler)]

        if phrased and input.tokens:
            without_stopwords = ' '.join(t for t in input.tokens if t not in self._stopwords)

            most_similar = self._sim_index.most_similar(
                intents=[h.phrases for h in phrased],
                text=without_stopwords
            )

            if most_similar is not None:
                phrased[most_similar].action()

                return

        youngest_otherwise = next((h for h in reversed(self._handlers) if isinstance(h, OtherwiseHandler)), None)

        if youngest_otherwise:
            youngest_otherwise.action()

            return

        self.append_reply("Я полохо тебя слышу. Подойти поближе и повтори ещё разок.")

    def _drop_outdated_handlers(self):
        """
        Отбрасывает неактуальные обработчики
        """
        self._handlers = [h for h in self._handlers if h.generation in (0, self._requests_count)]

    def _warmup_sim_index(self):
        """
        Энкодер может работать достаточно долго
        Так что переносим его работу на фазу после ответа
        """
        for h in self._handlers:
            match h:
                case PhraseHandler(phrases=p):
                    self._sim_index.add(p)

    def set_stopwords(self, words: Iterable[str]):
        self._stopwords = frozenset(words)
