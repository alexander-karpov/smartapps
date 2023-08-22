from dialoger import TextReply, Voice
from enrichment import random_hypernym
from morphy import by_gender
from stories.story import Story, StoryStep


class AtLessonStory(Story):
    """
    На паре географии учительница спрашивает:
    - Ребята, как называется большая пустыня в Африке?
    - Сахара! - отвечает один мальчик.
    - Отлично, а как называется самая глубокая бездна в океане?
    - Бермудский треугольник! - отвечает другой.
    - Неееет, - говорит учительница, - это не бездна, а географическое явление.
    На это мальчик в третьем ряду вспоминает ответ и восклицает:
    - А, я знаю! Кремлевский телеграф!
    Все класс рассмеялся, а учительница поняла, что вопросы из географии им нужно повторить еще раз.
    """

    _name: str
    _item: str

    def create_story_steps(self) -> list[StoryStep]:
        return [
            self.make_entity_step(
                "Назови любой предмет рядом с тобой или на улице.",
                lambda e: setattr(self, "_item", e.nomn),
            ),
            self.make_step(
                "Назови имя твоего друга или знакомого.",
                self._fill_name,
                unsuitable_input_message="Это не похоже на настоящее имя.",
            ),
            self._tell_story,
        ]

    async def _fill_name(self) -> bool:
        i = self._api.input()
        name = i.first_name or i.last_name

        if not name and i.entities():
            name = i.entities()[0].subject[0]

        if name:
            self._name = name

            return True

        return False

    async def _tell_story(self) -> None:
        item_hypernym = random_hypernym(self._item) or self._item
        fall_in_love = by_gender(self._name or "", "влюбил", "ся", "ась", "ось")
        name_it = by_gender(self._name or "", "", "он", "она", "оно")

        self._api.say(
            # "Вот одна история.",
            "Однажды на уроке географии учительница задает вопрос:",
            "- Ребята,",
            "как называется большая пустыня в Африке?",
            "- Сах+ара!",
            "- отвечает один мальчик.",
            "- Отлично, а как называется самая глубокая бездна в океане?",
            f"- {self._item}",
            " - отвечает другой.",
            "- Нет-нет,",
            "- говорит учительница,",
            f"{self._item} - это не бездна, а {item_hypernym}.",
            "На это девочка на третьем ряду встаёт и говорит:",
            f"- А я знаю! {self._name} – {fall_in_love}!",
            "Весь класс рассмеялся, а учительница поняла, что вопросы по географии нам нужно повторить еще раз.",
            "",
            TextReply(
                f"- {fall_in_love}? Прямо так и сказала?",
                voice=Voice.ZAHAR_GPU,
            ),
            f"- Да, именно так. И ничего {name_it} не {fall_in_love}.",
        )

        await self.goto_next_step()
