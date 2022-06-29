
from dataclasses import dataclass
from functools import lru_cache
from types import FunctionType
from typing import Callable

from smartapps.dialog.reply import Reply
from smartapps.dialog.input import Input
from smartapps.dialog.response_builder import ResponseBuilder
from smartapps.dialog.similarity_index import SimilarityIndex, similarity_index

@dataclass
class Handler:
    action: Callable[[], None]
    generation: int


@dataclass
class PhraseHandler(Handler):
    phrases: tuple[str, ...]


@dataclass
class TriggerHandler(Handler):
    trigger: Callable[[Input], bool]


@dataclass
class OtherwiseHandler(Handler):
    pass


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

#----------------------------------------------------------

def _create_hagi_dialog() -> Dialog:
    dialog = Dialog()
    on, say = dialog.append_handler, dialog.append_reply

    @on(lambda i: i.is_new_session)
    def _():
        say(
            ('Хаги - кукла из игры. Ожила так что беги.', 'Х+аги -- кукла из игры! Ожила - так что беги.'),
            # silence(500)
            'Я ХАГИ ВАГИ. Я буду играть с тобой в повторюшу.'
            # silence(500)
            'Но не зли меня!'
            # silence(500)
            'А теперь скажи что-нибудь.'
        )

    @on(lambda i: i.utterance in ('помощь', 'что ты умеешь'))
    def _():
        say(
            'Я живу на фабрике. Я умею прятаться и кусаться.',
            # silence(500)
            'Они научили меня играть в повторюшу.',
            # silence(500);
            'Я буду играть с тобой. Я повторю, что ты скажешь.',
            'Но не зли меня.',
            # silence(500);
            'И если ты подойдёшь слишком близко.',
            # silence(300);
            ('Я съем тебя!', 'Я - съем - теб+я!'),
            # silence(500);
            ('Если боишься, скажи «Выход».', 'Если боишься, скажи - - выход.'),
            # silence(500);
            'А теперь скажи что-нибудь.',
        )

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


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    return _create_hagi_dialog()
