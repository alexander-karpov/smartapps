from functools import lru_cache
from typing import Optional, Protocol
from dialoger import Dialog, TextReply, Voice
from dialoger.dialog_api import DialogAPI
from enrichment import add_random_adjective
from entity_parser import Entity


class Story(Protocol):
    def tell_story(self, api: DialogAPI) -> None:
        ...


class AtTheLessonStory:
    _name: Optional[str]
    _fruit: Optional[str]

    def tell_story(self, api: DialogAPI) -> None:
        self._ask_fruit(api)

    def _ask_fruit(self, api: DialogAPI) -> None:
        api.say("Назови что-нибудь съедобное")

        @api.trigger(lambda i: i.entities())
        async def _(entities: list[Entity]):
            fruit = entities[0].nomn
            self._fruit = await add_random_adjective(fruit)

            self._ask_name(api)

        @api.otherwise
        def _():
            api.say("Ой! Я немного отвлеклась. Что ты говоришь?")

            self._ask_fruit(api)

    def _ask_name(self, api: DialogAPI) -> None:
        api.say("Назови имя твоего друга или знакомого")

        @api.otherwise
        def _():
            self._name = api.input().first_name

            api.say(
                "Однажды у нас на уроке географии учительница спрашивает:",
                "\n- Ребята,",
                "как называется большая пустыня в Африке?",
                "\n- Сах+ара!" " - отвечает один мальчик.",
                "\n- Отлично, а как называется самая глубокая бездна в океане?",
                "\n- Бермудский треугольник!",
                " - отвечает другой.",
                "\n- Нет-нет",
                ", - говорит учительница,",
                " - это не бездна, а географическое явление.",
                f"И тут {self._name} на третьем ряду вспоминает ответ, встаёт и говорит:",
                f"\n- А! Я знаю! Это {self._fruit}!",
                "\nВесь класс рассмеялся, а учительница поняла, что пора перекусить",
            )


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=["алиса"])
    api = DialogAPI(dialog)

    stories: list[Story] = [AtTheLessonStory()]

    @api.new_session
    def _():
        api.say(
            "Привет. С тобой часто приключаются весёлые истории? Со мной – постоянно. Хочешь, расскажу тебе что-нибудь?",
            "Их очень много и все они – чистая правда. Но чтобы их вспомнить, мне нужна твоя помощь.",
            "Я буду задавать тебе вопросы. Твои ответы помогут мне вспомнить что-то интересное. Начинаем?",
        )

        # 🔥 button

        @api.otherwise
        def _():
            story = stories[0]
            story.tell_story(api)

    return dialog
