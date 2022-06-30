from types import FunctionType
from typing import Callable
from dialoger.handler import Handler, OtherwiseHandler, PhraseHandler, TriggerHandler
from dialoger.reply import Reply
from dialoger.input import Input
from dialoger.response_builder import ResponseBuilder
from dialoger.similarity_index import SimilarityIndex, similarity_index


class Dialog:
    _sim_index: SimilarityIndex
    _handlers: list[Handler]
    _replies: list[Reply]
    _handlers_generation: int
    _input: Input | None
    _postproc: Callable[[list[Reply]], list[Reply]] | None

    def __init__(self) -> None:
        self._handlers = []
        self._sim_index = similarity_index
        self._handlers_generation = 0
        self._replies = []
        self._postproc = None

    def handle_request(self, request: dict) -> dict:
        response_builder = ResponseBuilder()
        input = Input(request)

        if input.is_ping:
            response_builder.append_text("Pong!")
            response_builder.end_session()
        else:
            self._generate_response(input)

        self._replies_to_response(response_builder)

        return response_builder.build()

    def _replies_to_response(self, response_builder: ResponseBuilder):
        if self._postproc:
            self._replies = self._postproc(self._replies)

        for reply in self._replies:
            reply.append_to(response_builder)

    def after_response(self):
        self._input = None
        self._update_handlers()

    def _generate_response(self, input: Input) -> None:
        self._input = input
        self._replies = []

        triggered = next((h for h in self._handlers if isinstance(h, TriggerHandler) and h.trigger(input)), None)

        if triggered:
            triggered.action()

            return

        phrased = [h for h in self._handlers if isinstance(h, PhraseHandler)]

        if phrased and input.utterance:
            most_similar = self._sim_index.most_similar(
                intents=[h.phrases for h in phrased],
                text=input.utterance
            )

            if most_similar is not None:
                phrased[most_similar].action()

                return

        youngest_otherwise = next((h for h in reversed(self._handlers) if isinstance(h, OtherwiseHandler)), None)

        if youngest_otherwise:
            youngest_otherwise.action()

            return

        self.append_reply("Я полохо тебя слышу. Подойти поближе и повтори ещё разок.")

    def _update_handlers(self):
        self._handlers = [h for h in self._handlers if h.generation in (0, self._handlers_generation)]
        self._handlers_generation += 1

    def append_handler(self, intent: str | Callable[[Input], bool] | None = None):
        def decorator(action: Callable[[], None]):
            match intent:
                case str():
                    self._handlers.append(PhraseHandler(
                        phrases=tuple(phrase.strip() for phrase in intent.lower().split(',')),
                        action=action,
                        generation=self._handlers_generation,
                    ))
                case FunctionType():
                    self._handlers.append(TriggerHandler(
                        trigger=intent,
                        action=action,
                        generation=self._handlers_generation,
                    ))
                case _:
                    self._handlers.append(OtherwiseHandler(
                        action=action,
                        generation=self._handlers_generation,
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

    def postproc(self, fn: Callable[[list[Reply]], list[Reply]]):
        self._postproc = fn

        return fn
