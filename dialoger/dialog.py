
from dataclasses import dataclass
from functools import lru_cache
from types import FunctionType
from typing import Callable
from dialoger.handler import Handler, OtherwiseHandler, PhraseHandler, TriggerHandler

from dialoger.reply import Reply
from dialoger.input import Input
from dialoger.response_builder import ResponseBuilder
from dialoger.similarity_index import SimilarityIndex, similarity_index




class Dialog:
    _handlers: list[Handler]
    _sim_index: SimilarityIndex
    _response_builder: ResponseBuilder
    _handlers_generation: int

    def __init__(self) -> None:
        self._handlers = []
        self._sim_index: SimilarityIndex = similarity_index
        self._handlers_generation = 0

    def handle_request(self, request: dict) -> dict:
        self._response_builder = ResponseBuilder()
        input = Input(request)

        if input.is_ping:
            self._response_builder.append_text("Pong!")
            self._response_builder.end_session()
        else:
            self._generate_response(input)

        return self._response_builder.build()

    def after_response(self):
        self._update_handlers()

    def _generate_response(self, input: Input) -> None:
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

        self._response_builder.append_text("Я полохо тебя слышу. Подойти поближе и повтори ещё разок.")

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
                    reply.append_to(self._response_builder)
                case _:
                    Reply(reply).append_to(self._response_builder)
