from dialoger import Dialog

def append_help(dialog: Dialog) -> None:
    on, say = dialog.append_handler, dialog.append_reply

    @on(trigger=lambda i: i.utterance in ('помощь', 'что ты умеешь'))
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
