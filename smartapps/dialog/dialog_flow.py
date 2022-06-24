
from dataclasses import dataclass
from typing import List, Optional, Protocol
from smartapps.dialog.intent import Intent
from smartapps.dialog.reply import Reply
from smartapps.dialog.input import Input
from smartapps.dialog.response_builder import ResponseBuilder

@dataclass
class ResponseCandidate:
    body: Reply
    has_continuation: bool


class ResponseGenerator(Protocol):
    def generate(self, input: Input) -> Optional[ResponseCandidate]:
        ...

    def save_changes(self) -> None:
        ...


class Transition(Protocol):
    def trigger(self, input: Input) -> bool:
        ...

    def effect(self) -> 'TransitionEffect':
        ...


@dataclass
class TransitionEffect:
    reply: Reply
    transitions: List[Transition]


class ScriptedResponseGenerator(ResponseGenerator):
    _start: Transition
    _transitions: List[Transition]
    _changes: Optional[TransitionEffect]
    _in_progress: bool = False

    def __init__(self, start: Transition):
        self._start = start
        self._transitions = [start]

    def generate(self, input: Input) -> Optional[ResponseCandidate]:
        self._changes = None
        triggered = next((t for t in self._transitions if t.trigger(input)), None)

        if triggered is None:
            return None

        self._changes = triggered.effect()

        return ResponseCandidate(self._changes.reply, bool(self._changes.transitions))

    def save_changes(self) -> None:
        assert self._changes

        self._transitions = self._changes.transitions
        self._in_progress = True
        self._changes = None

    @property
    def in_progress(self) -> bool:
        return self._in_progress


class Dialog:
    _response_generators: list[ResponseGenerator]

    def __init__(self, response_generators: list[ResponseGenerator]) -> None:
        self._response_generators = response_generators

    def handle_request(self, request: dict) -> dict:
        response_builder = ResponseBuilder()
        input = Input(request)

        if input.is_ping:
            response_builder.append_text("Pong!")
            response_builder.end_session()
        else:
            self.update(input, response_builder)

        return response_builder.build()

    def update(self, input: Input, response_builder: ResponseBuilder) -> None:
        for rg in self._response_generators:
            candidate = rg.generate(input)

            if candidate:
                candidate.body.append_to(response_builder)
                rg.save_changes()
                return

        response_builder.append_text("Sorry, I don't understand.")

#----------------------------------------------------------

class HagiGreatingTransition(Transition):
    def trigger(self, input: Input) -> bool:
        return input.utterance == 'привет'

    def effect(self) -> TransitionEffect:
        return TransitionEffect(Reply('Привет, человечик. Хочешь поиграть со мной?', ('👻', '. р-р-р!')), [
            YesTransition(), NoTransition()
        ])

class NoTransition(Transition):
    def trigger(self, input: Input) -> bool:
        return Intent('нет', 'я боюсь', 'ты меня съешь').match(input.utterance)

    def effect(self) -> 'TransitionEffect':
        return TransitionEffect(Reply('Не надо бояться. Сначала я с тобой поиграю.'), transitions=[])


class YesTransition(Transition):
    def trigger(self, input: Input) -> bool:
        return Intent('да', 'хочу', 'во что будем играть').match(input.utterance)

    def effect(self) -> 'TransitionEffect':
        return TransitionEffect(Reply('Я люблю играть в прятки. Ты готов прятаться?'), transitions=[])


class EchoResponseGenerator(ResponseGenerator):
    def generate(self, input: Input) -> ResponseCandidate | None:
        return ResponseCandidate(Reply(input.utterance), False)

    def save_changes(self) -> None:
        pass


dialog = Dialog([
    ScriptedResponseGenerator(start=HagiGreatingTransition()),
    EchoResponseGenerator(),
])
