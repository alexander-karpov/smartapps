from functools import lru_cache
from dialoger import Dialog
from hagi.append_chitchat import append_chitchat


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

    append_chitchat(dialog)

    return dialog


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    return _create_hagi_dialog()
