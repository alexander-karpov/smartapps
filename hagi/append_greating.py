
from dialoger import Dialog

def append_greating(dialog: Dialog) -> None:
    on, say = dialog.append_handler, dialog.append_reply

    @on(trigger=lambda i: i.is_new_session)
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

        @on("что-нибудь")
        def _():
            say('Хороший человечик. Приходи играть ко мне на фабрику')
