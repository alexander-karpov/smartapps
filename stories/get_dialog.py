from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Optional
from dialoger import Dialog, TextReply, Voice

class Field:
    name: str
    value: Optional[str]

    def __init__(self, name: str) -> None:
        self.name = name
        self.value = None

    def __str__(self) -> str:
        assert self.value, 'Поле заполнено'

        return self.value

class Story(ABC):
    fields: list[Field]

    def __init__(self) -> None:
        self.fields = []
        pass

    @abstractmethod
    def append_to(self, dialog: Dialog) -> None:
        '''
        Добавляет историю в ответ диалога
        '''

    def next_empty_field(self) -> Optional[Field]:
        for f in self.fields:
            if f.value is None:
                return f
            
        return None

class AtTheLessonStory(Story):
    def __init__(self) -> None:
        super().__init__()

        self.fields.extend([Field('имя друга'), Field('имя знакомого'), Field('любимое место')])

        pass
    
    def append_to(self, dialog: Dialog) -> None:
        assert self.next_empty_field() is None, 'Все поля заполнены'

        say = dialog.append_reply
        [friend_name, some_name, place] = self.fields

        say(
            'На уроке географии учительница спрашивает',
            TextReply(
                '\n- Ребята,',
                ('','sil <[300]>'),
                'как называется большая пустыня в Африке?',
                voice=Voice.OKSANA_GPU
            ),
            TextReply(('\n- Сахара!', 'Сах+ара!'), voice=Voice.KOSTYA_GPU),
            f' - отвечает мальчик {friend_name}.',
            TextReply('\n- Отлично, а как называется самая глубокая бездна в океане?', voice=Voice.OKSANA_GPU),
            TextReply('\n- Бермудский треугольник!', voice=Voice.KOLYA_GPU),
            f' - отвечает {some_name}.',
            TextReply('\n- Нет-нет-нет.', voice=Voice.OKSANA_GPU),
            ', - говорит учительница,',
            TextReply(' - это не бездна, а географическое явление.', voice=Voice.OKSANA_GPU),
            'На это мальчик в третьем ряду вспоминает ответ и восклицает:',
            TextReply(f'\n- А, я знаю! {place}!', voice=Voice.ZAHAR_GPU),
            'Весь класс рассмеялся, а учительница поняла, что вопросы из географии им нужно повторить еще раз.'
        )

@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=['алиса'])
    on, say, input = dialog.append_handler, dialog.append_reply, dialog.input

    story = AtTheLessonStory()

    @on()
    async def _():
        field = story.next_empty_field()
        utterance = input().utterance

        if utterance and field:
            field.value = utterance

        field = story.next_empty_field()

        if field:
            say('Назови ', field.name)
        else:
            story.append_to(dialog)
            say('Вот такая история.')
        

    return dialog
