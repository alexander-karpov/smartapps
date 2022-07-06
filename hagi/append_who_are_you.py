from dialoger import Dialog
import random

def append_who_are_you(dialog: Dialog) -> None:
    on, say, prompt = dialog.append_handler, dialog.append_reply, dialog.append_prompt

    @prompt()
    def _():
        say(random.choice((
            'А хочешь знать кто я такой?',
            'Хочешь расскажу свою историю?',
            'Рассказать как я стал таким?',
        )))

        on('да','хочу', 'давай',  'расскажи', 'да можно да хочу хочу расскажи историю')(
            who_are_you
        )

    @on(
        'скажи кто такой ты',
        'ты кто вообще',
        'а ты кто',
        'расскажи про себя',
        'расскажи свою историю',
        'расскажи историю почему ты стал живым',
    )
    def who_are_you():
        if random.choice((1, 1, 0)):
            say(random.choice((
                'Хочешь знать про меня?',
                'Сказать, кто я?',
            )))

        say(random.choice((
            'Я – Х+аги, меня сделали чтобы обниматься.',
            'Я кукла из игры. Я был мягкий и добрый.',
            'У меня большие руки. Я обнимал человечков.',
            'Я синий и мягкий. Я был хорошим.',
        )))

        say(random.choice((
            'Но потом начались эксперименты.',
            'Но им не нужен был хороший Х+аги.',
            'Они хотели сделать меня плохим. Но у них не получилось.',
        )))

        say(random.choice((
            'Теперь я всегда голодный.',
            'Теперь я прячусь.',
            'Теперь меня боятся.',
            'Теперь со мной не играют.',
            'Теперь я умею кушать.',
        )))

        say(random.choice((
            'А ты кто?',
            'Я плохо помню. Ты знаешь мою историю? Расскажи'
            'Ты тоже расскажи о себе, человечик.',
            'Как думаешь, зачем они это сделали?',
            'Как думаешь, я смогу снова стать добрым?',
            'Я думаю, К+иси М+иси может мне помочь. Ты знаешь её?',
            'А ты маленький вкусный человечик.',
        )))
