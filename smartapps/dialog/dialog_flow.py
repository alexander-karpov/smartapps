
from dataclasses import dataclass
from typing import Callable, List, Optional, Protocol, TypeAlias
from smartapps.dialog.intent import Intent
from smartapps.dialog.reply import Reply
from smartapps.dialog.input import Input
from smartapps.dialog.response_builder import ResponseBuilder
from smartapps.dialog.similarity_index import SimilarityIndex, similarity_index


@dataclass
class ResponseCandidate:
    body: Reply
    has_continuation: bool


class ResponseGenerator(Protocol):
    def generate(self, input: Input) -> Optional[ResponseCandidate]:
        ...

    def save_changes(self) -> None:
        ...



Trigger: TypeAlias = str
ScriptStage: TypeAlias = dict[Trigger, 'ScriptTransition']

@dataclass
class ScriptTransitionData:
    reply: Reply
    stage: ScriptStage

ScriptTransition: TypeAlias = Callable[[Input], ScriptTransitionData]


class ScriptedResponseGenerator(ResponseGenerator):
    _start: ScriptTransition
    _transitions: dict[str, ScriptTransition]
    _changes: Optional[TransitionEffect]
    _in_progress: bool = False
    similarity: SimilarityIndex = similarity_index

    def __init__(self, start: ScriptTransition):
        self._start = start
        self._transitions = [start]

    def generate(self, input: Input) -> Optional[ResponseCandidate]:
        self._changes = None

        most_similar = self.similarity.most_similar(
            intents=[tran.trigger(input).samples for tran in self._transitions],
            text=input.utterance
        )

        if most_similar is None:
            return None

        self._changes = self._transitions[most_similar].effect()

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

class HagiGreatingTransition(ScriptTransition):
    def trigger(self, input: Input) -> Intent:
        return Intent('привет', 'привет хаги ваги')

    def effect(self) -> TransitionEffect:
        return TransitionEffect(Reply('Привет, человечик. Хочешь поиграть со мной?', ('👻', '. р-р-р!')), [
            YesTransition(), NoTransition()
        ])

class NoTransition(ScriptTransition):
    def trigger(self, input: Input) -> Intent:
        return Intent('нет', 'я боюсь', 'ты меня съешь')

    def effect(self) -> 'TransitionEffect':
        return TransitionEffect(Reply('Не надо бояться. Сначала я с тобой поиграю.'), transitions=[GameTransition()])


class YesTransition(ScriptTransition):
    def trigger(self, input: Input) -> Intent:
        return Intent('да', 'хочу', 'во что будем играть')

    def effect(self) -> 'TransitionEffect':
        return TransitionEffect(Reply('Я люблю играть в прятки. Ты готов прятаться?'), transitions=[GameTransition()])

class GameTransition(ScriptTransition):
    def trigger(self, input: Input) -> Intent:
        return Intent('готов', 'да', 'я спрятался')

    def effect(self) -> 'TransitionEffect':
        return TransitionEffect(Reply('Раз. Два. Пять. Я иду искать. Ку-ку'), transitions=[])



class EchoResponseGenerator(ResponseGenerator):
    def generate(self, input: Input) -> ResponseCandidate | None:
        return ResponseCandidate(Reply(input.utterance), False)

    def save_changes(self) -> None:
        pass


_dialog = Dialog([
    ScriptedResponseGenerator(start=HagiGreatingTransition()),
    EchoResponseGenerator(),
])

def get_dialog(request:dict) -> Dialog:
    global _dialog

    if request["session"]["new"]:
        _dialog = Dialog([
            ScriptedResponseGenerator(start=HagiGreatingTransition()),
            EchoResponseGenerator(),
        ])

    return _dialog


def hello(reply, on):
    @on('да')
    def _():
        reply('Давай играть. Во что будем играть?')

        @on('Прятки')
        def _():
            reply('Я хорошо ищу. Ты спрятался?')

            @on('да')
            def _():
                reply('А я тебя уже съел. Ам!')

            @on('нет')
            def _():
                reply('Вот и зря. Ам!')

        @reply('Вышибала')
        def _(): reply('Тогла лови мячик. Поймал?')

    @on('нет')
    def _():
        return 'Ну как хочешь'
