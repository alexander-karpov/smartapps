
from dataclasses import dataclass
from typing import Callable

from traitlets import default
from smartapps.dialog.reply import Reply
from smartapps.dialog.input import Input
from smartapps.dialog.response_builder import ResponseBuilder
from smartapps.dialog.similarity_index import SimilarityIndex, similarity_index

@dataclass
class Handler:
    intent: tuple[str, ...] | None
    action: Callable[[], None]
    generation: int
    otherwise: bool


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
        with_intent = [h for h in self._handlers if h.intent]

        most_similar = self._sim_index.most_similar(
            intents=[h.intent for h in with_intent if h.intent],
            text=input.utterance
        ) if with_intent else None

        if most_similar is not None:
            with_intent[most_similar].action()

            return

        youngest_otherwise = next((h for h in reversed(self._handlers) if h.otherwise), None)

        if youngest_otherwise:
            youngest_otherwise.action()

            return

        self._response_builder.append_text("Я полохо тебя слышу. Подойти поближе и повтори ещё разок.")

    def _update_handlers(self):
        self._handlers = [h for h in self._handlers if h.generation in (0, self._handlers_generation)]
        self._handlers_generation += 1

    def append_handler(self, intent: str | None = None):
        def decorator(action: Callable[[], None]):
            self._handlers.append(Handler(
                intent=
                    tuple(phrase.strip() for phrase in intent.lower().split(','))
                    if intent else None,
                action=action,
                generation=self._handlers_generation,
                otherwise=not intent
            ))

            return action

        return decorator

    def append_reply(self, reply: str | tuple[str,str] | Reply ):
        match reply:
            case Reply():
                reply.append_to(self._response_builder)
            case _:
                Reply(reply).append_to(self._response_builder)

#----------------------------------------------------------

def create_hagi_dialog() -> Dialog:
    dialog = Dialog()
    on, say = dialog.append_handler, dialog.append_reply

    @on('привет, здравтвуйте, привет хаги ваги')
    def _():
        say('Привет, человечик')

    @on('ты хороший, ты молодец')
    def _():
        say('Ты тоже. Ты вкусный')

    @on('давай играть, хочешь поиграть, я хочу с тобой поиграть')
    def _():
        say('Я люблю играть с человечками в догонялки и в прятки')

        @on('в догонялки, догони меня')
        def _():
            say('Я догнал тебя. Ам!')

        @on('в прятки, я спрятался, попробуй найди меня')
        def _():
            say('Я нашёл тебя. Ам!')

        @on()
        def _():
            say('Я не знаю такую игру ')

    @on()
    def _():
        say('Уходи!')

    return dialog


_dialog = create_hagi_dialog()

def get_dialog(request:dict) -> Dialog:
    global _dialog

    if request["session"]["new"]:
        _dialog = create_hagi_dialog()

    return _dialog
