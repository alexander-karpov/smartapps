from functools import lru_cache
from dialoger import Dialog, TextReply, Voice


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=['алиса'])
    on, say = dialog.append_handler, dialog.append_reply

    @on()
    async def _():
        say(
            'На уроке географии учительница спрашивает',
            TextReply(
                '\n- Ребята,',
                ('','sil <[300]>'),
                'как называется большая пустыня в Африке?',
                voice=Voice.OKSANA_GPU
            ),
            TextReply(('\n- Сахара!', 'Сах+ара!'), voice=Voice.KOSTYA_GPU),
            ' - отвечает один мальчик.',
            TextReply('\n- Отлично, а как называется самая глубокая бездна в океане?', voice=Voice.OKSANA_GPU),
            TextReply('\n- Бермудский треугольник!', voice=Voice.VALTZ_GPU),
            ' - отвечает другой.',
            TextReply('\n- Не-е-е-ет', voice=Voice.OKSANA_GPU),
            ', - говорит учительница,',
            TextReply(' - это не бездна, а географическое явление.', voice=Voice.OKSANA_GPU),
            'На это мальчик в третьем ряду вспоминает ответ и восклицает:',
            TextReply('\n- А, я знаю! Кремлевский телеграф! ', voice=Voice.ZAHAR_GPU),
            'Весь класс рассмеялся, а учительница поняла, что вопросы из географии им нужно повторить еще раз.'
        )

    return dialog
