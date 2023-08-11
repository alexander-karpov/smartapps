from functools import lru_cache
from typing import Optional, Protocol
from dialoger import Dialog, TextReply, Voice
from enrichment import add_random_adjective
from morphy import to_nomn
from entity_parser import parse_entity


class Story(Protocol):
    def tell_story(self, dialog: Dialog) -> None:
        ...


class AtTheLessonStory:
    _name: Optional[str]
    _fruit: Optional[str]

    def tell_story(self, dialog: Dialog) -> None:
        on, say, input = dialog.append_handler, dialog.append_reply, dialog.input

        say("Назови твой любимый фрукт или овощ.")

        @on()
        async def _():
            entities = parse_entity(input().utterance)
            fruit = entities[0].nomn if entities else to_nomn(input().tokens[-1])

            self._fruit = await add_random_adjective(fruit)

            say("А теперь имя твоего друга или знакомого.")

            @on()
            def _():
                self._name = input().first_name

                say(
                    "Однажды у нас на уроке географии учительница спрашивает:",
                    TextReply(
                        "\n- Ребята,",
                        ("", "sil <[300]>"),
                        "как называется большая пустыня в Африке?",
                        voice=Voice.OKSANA_GPU,
                    ),
                    TextReply(("\n- Сахара!", "Сах+ара!"), voice=Voice.KOSTYA_GPU),
                    " - отвечает один мальчик.",
                    TextReply(
                        "\n- Отлично, а как называется самая глубокая бездна в океане?",
                        voice=Voice.OKSANA_GPU,
                    ),
                    TextReply("\n- Бермудский треугольник!", voice=Voice.KOLYA_GPU),
                    " - отвечает другой.",
                    TextReply("\n- Нет-нет-нет", voice=Voice.OKSANA_GPU),
                    ", - говорит учительница,",
                    TextReply(
                        " - это не бездна, а географическое явление.",
                        voice=Voice.OKSANA_GPU,
                    ),
                    f"И тут {self._name} на третьем ряду вспоминает ответ, встаёт и говорит:",
                    TextReply(f"\n- А, я знаю! {self._fruit}!", voice=Voice.ZAHAR_GPU),
                    "\nВесь класс рассмеялся, а учительница поняла, что вопросы из географии нам лучше не задавать.",
                )


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=["алиса"])
    on, say, input = dialog.append_handler, dialog.append_reply, dialog.input

    stories: list[Story] = [AtTheLessonStory()]

    @on(trigger=lambda i: i.is_new_session)
    def _():
        say(
            "Привет. С тобой часто приключаются весёлые истории? Со мной – постоянно. Хочешь, расскажу тебе что-нибудь?",
            "Их очень много и все они – чистая правда. Но чтобы их вспомнить, мне нужна твоя помощь.",
            "Я буду задавать тебе вопросы. Твои ответы помогут мне вспомнить что-то интересное. Начинаем?",
        )

        # 🔥 button

        @on("начинай", including_yes=True)
        def _():
            story = stories[0]
            story.tell_story(dialog)

    return dialog
