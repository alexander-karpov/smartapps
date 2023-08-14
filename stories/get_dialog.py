from functools import lru_cache
from typing import Optional
from dialoger import Dialog, TextReply, Voice, DialogAPI
from enrichment import add_random_adjective
from morphy import by_gender, inflect
from stories.story import Story


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
    _fruit: str

    def create_steps(self):
        return [
            self.make_step("Назови имя твоего друга или знакомого", self._fill_name),
            self.make_step("Назови что-нибудь съедобное", self._fill_fruit),
            self._tell_story,
        ]

    async def _fill_fruit(self) -> bool:
        entities = self._api.input().entities()

        if entities:
            fruit = entities[0].nomn
            self._fruit = await add_random_adjective(fruit, "nomn")

            return True

        return False

    async def _fill_name(self) -> bool:
        i = self._api.input()
        name = i.first_name or i.last_name

        if name:
            self._name = name

        return bool(self._name)

    def _tell_story(self) -> None:
        self._api.say(
            "Вот одна история.",
            "Однажды на уроке географии учительница задает вопрос:",
            "- Ребята,",
            "как называется большая пустыня в Африке?",
            "- Сах+ара!",
            " - отвечает один мальчик.",
            "- Отлично, а как называется самая глубокая бездна в океане?",
            "- Бермудский треугольник!",
            " - отвечает другой.",
            "- Нет-нет",
            ", - говорит учительница,",
            " - это не бездна, а географическое явление.",
            f"И тут {self._name} на третьем ряду вспоминает ответ и говорит:",
            f"- А! Я знаю! Это {self._fruit}!",
            "Весь класс рассмеялся, а учительница поняла, что вопросы по географии нам нужно повторить еще раз.",
            "",
            TextReply(
                f"- {self._fruit}? Прямо так и {by_gender(self._name or '', 'сказал', '', 'а', 'о')}?",
                voice=Voice.ZAHAR_GPU,
            ),
            "- Да, именно так, чистая правда.",
        )

        self.goto_next_step()


class InZooStory(Story):
    """
    Однажды в полночь в зоопарк решили наведаться трое друзей - Вася, Петя и Миша. Они забрались через забор, чтобы пообщаться с животными, когда все работники уже ушли.
    Внезапно, из ниоткуда появилась смотрительница зоопарка - страшная старуха с косой.
    Друзья в ужасе сели на первую попавшуюся скамейку и тут же притворились статуями, надеясь, что смотрительница их не заметит.
    Старуха медленно идет в их сторону, осматривая пустующий зоопарк. Подойдя ближе, она глядит на "статуи" и кричит: "Ага, я вас разоблачу!"
    Она подходит к Васе и спрашивает: "Ты статуя?"
    Вася не моргая отвечает на скорую руку:
    - нет, я носорог даже если я и не двигаюсь
    Смотрительница хмуро кивает и идет к Пете:
    - А ты статуя?
    Петя ответил в тон:
    - Нет, я равнодушный леопард, и даже если я и не двигаюсь, это значит, что я не ем.
    Смотрительница на минуту задумалась, почесала косой по дереву, а затем идет к Мише и спрашивает:
    - Так и ты, наверное, тоже не статуя?
    Миша отвечает:
    - Я, правда, статуя! Но до сих пор мог напугать вас своим гипсаком, когда мои друзья уже отвергали вас.
    Смотрительница выдала лающий смех и злостно продолжала поиск воришек. И хотя друзья встретились с превратностями и обладали оригинальными оправданиями, решение провести ночь на свободе было жизнью сохранено.
    После этого случая страх повстречать смотрительницу в полночь заставил их глубоко переосмыслить идею проведения непредумышленных ночных прогулок в зоопарке.
    """

    _animal: str
    _wild_animal: str
    _item: str

    def create_steps(self):
        return [
            self.make_step("Назови какое-нибудь животное", self._fill_animal),
            self.make_step(
                "Теперь назови какое-нибудь животное с острыми зубами",
                self._fill_wild_animal,
            ),
            self.make_step(
                "Назови любой предмет рядом с тобой или на улице", self._fill_item
            ),
            self._tell_story,
        ]

    async def _fill_animal(self) -> bool:
        entities = self._api.input().entities()

        if entities:
            self._animal = entities[0].subject[0]

            return True

        return False

    async def _fill_wild_animal(self) -> bool:
        entities = self._api.input().entities()

        if entities:
            self._wild_animal = entities[0].subject[0]

            return True

        return False

    async def _fill_item(self) -> bool:
        entities = self._api.input().entities()

        if entities:
            self._item = entities[0].subject[0]

            return True

        return False

    def _tell_story(self) -> None:
        animal_ablt_plur = inflect(self._animal or "носорог", ({"ablt", "plur"},))
        item_ablt_plur = inflect(self._item or "статуя", ({"ablt", "plur"},))

        self._api.say(
            "Вспомнила историю.",
            "Однажды в полночь в зоопарк решили наведаться трое друзей - Вася, Петя и Миша.",
            f"Они забрались через забор, чтобы пообщаться с {animal_ablt_plur}, когда все работники уже ушли.",
            "Внезапно, из ниоткуда появилась смотрительница зоопарка - страшная старуха с косой.",
            f"Друзья в ужасе сели на первую попавшуюся скамейку и тут же притворились {item_ablt_plur}, надеясь, что смотрительница их не заметит.",
            "",
            TextReply(
                f"- Притворились {item_ablt_plur}? Хотел бы я на это посмотреть.",
                voice=Voice.ZAHAR_GPU,
            ),
            "- От страха ещё не так притворишься. Рассказать, что было дальше?",
        )

        # 🔥 button дальше

        @self._api.otherwise
        async def _():
            item_accs_plur = inflect(self._item or "статуя", ({"accs", "plur"},))
            animal_adj = await add_random_adjective(self._animal, "nomn")
            wild_animal_adj = await add_random_adjective(self._wild_animal, "nomn")

            self._api.say(
                f"Старуха медленно идет в их сторону, осматривая пустующий зоопарк. Подойдя ближе, она глядит на «{item_accs_plur}» и кричит:",
                "-Ага! Я вас разоблачу!",
                "Она подходит к Васе и спрашивает:",
                f"- Ты {self._item}?",
                "Вася не моргая отвечает на скорую руку:"
                f"- Нет, я {animal_adj}, даже если я и не двигаюсь.",
                "Старуха подходит к Пете:",
                f"- А ты {self._item}?",
                "Петя ответил в тон:",
                f"- Нет, я {wild_animal_adj} и могу вас укусить.",
                "",
                TextReply(
                    "- Надеюсь, Петя не укусил бедную бабушку?",
                    voice=Voice.ZAHAR_GPU,
                ),
                "- К счастью, нет, не укусил. Рассказать, что было дальше?",
            )

            @self._api.otherwise
            async def _():
                item_nomn_plur = inflect(self._item or "статуя", ({"nomn", "plur"},))
                item_adj = await add_random_adjective(self._item, "nomn")
                common_item = by_gender(self._item, "обычн", "ый", "ая", "ое")

                self._api.say(
                    "Смотрительница на минуту задумалась, почесала косой по дереву, а затем идет к Мише и спрашивает:",
                    f"- Так и ты, наверное, тоже не {self._item}?",
                    "Миша отвечает:",
                    f"- Я, правда, {common_item} {item_adj}!",
                    "Смотрительница от злости выдала жуткий лающий смех и продолжала поиск воришек.",
                    "После этого случая, страх повстречать смотрительницу заставил их получше подумать, стоит ли гулять в зоопарке ночью.",
                    TextReply(
                        f"- Жуткая история. Мне теперь всю ночь будут {item_nomn_plur} сниться.",
                        voice=Voice.ZAHAR_GPU,
                    ),
                    "- Да. До сих пор не пойму, как им удалось меня обмануть.",
                )

                self.goto_next_step()


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=["алиса"])
    api = DialogAPI(dialog)

    stories: list[Story] = [AtLessonStory(api), InZooStory(api)]

    @api.new_session
    def _():
        api.say(
            "Привет. С тобой часто приключаются весёлые истории? Со мной – постоянно. Хочешь, расскажу тебе что-нибудь?",
            "Историй очень много и все они – чистая правда. Но чтобы их вспомнить, мне нужна твоя помощь.",
            "Я буду задавать тебе вопросы. Твои ответы помогут мне вспомнить что-то интересное. Начинаем?",
        )

        # 🔥 button дальше

        def end_current_story():
            api.say("Вот такая история.")

            if stories:
                api.say("Хочешь послушать ещё одну?")

                api.otherwise(start_next_story)
            else:
                api.say(
                    TextReply("Тут и сказки конец. А кто слушал – молодец", end=True)
                )

        def start_next_story():
            story = stories.pop(0)

            if story:
                story.start(end_current_story)
            else:
                api.say(
                    TextReply(
                        "Ой! Кажется, у меня молоко убежало! Мне пора. Пока, бавый",
                        end=True,
                    )
                )

        api.otherwise(start_next_story)

    return dialog


"""


1. Извини, отвлекся, повторишь?
2. Прошу прощения, не расслышал. Скажи еще раз?
3. Ой, задумался, повтори, пожалуйста?
4. Извини, не уловил, еще раз, пожалуйста?
5. Прости, пропустил, что сказал?
6. Не слышал, мог бы повторить?
7. Опять, пожалуйста, отвлекся.

Context: [ p:1989 c:145 t:2134 ]

© ChatGPT-4.0
"""
