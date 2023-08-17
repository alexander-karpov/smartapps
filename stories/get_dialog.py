from functools import lru_cache
from dialoger import Dialog, TextReply, Voice, DialogAPI
from enrichment import add_random_adjective, random_hypernym
from morphy import by_gender, inflect
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

        if name:
            self._name = name

            return True

        return False

    async def _tell_story(self) -> None:
        item_hypernym = random_hypernym(self._item) or self._item
        fall_in_love = by_gender(self._name or "", "влюбил", "ся", "ась", "ось")
        name_it = by_gender(self._name or "", "", "он", "она", "оно")

        self._api.say(
            "Вот одна история.",
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

    def create_story_steps(self):
        return [
            self.make_entity_step(
                "Назови какое-нибудь животное.",
                lambda i: setattr(self, "_animal", i.subject[0]),
            ),
            self.make_entity_step(
                "Теперь назови какое-нибудь животное с острыми зубами.",
                lambda i: setattr(self, "_wild_animal", i.subject[0]),
            ),
            self.make_entity_step(
                "Назови любой предмет рядом с тобой или на улице.",
                lambda i: setattr(self, "_item", i.subject[0]),
            ),
            self._tell_story,
        ]

    def _tell_story(self) -> None:
        animal_ablt_plur = inflect(self._animal or "носорог", ({"ablt", "plur"},))
        item_ablt_plur = inflect(self._item, ({"ablt", "plur"},))

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
            item_accs_plur = inflect(self._item, ({"accs", "plur"},))
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
                item_nomn_plur = inflect(self._item, ({"nomn", "plur"},))
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

                await self.goto_next_step()


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    """
    Создаёт новый диалог «Самые смешные истории»
    """
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

        async def end_current_story():
            api.say("Вот такая история.")

            if stories:
                api.say("Хочешь послушать ещё одну?")

                api.otherwise(start_next_story)
            else:
                api.say(
                    TextReply("Тут и сказки конец. А кто слушал – молодец", end=True)
                )

        async def start_next_story():
            story = stories.pop(0)

            if story:
                await story.start(end_current_story)
            else:
                api.say(
                    TextReply(
                        "Ой! Кажется, у меня молоко убежало! Мне пора. Пока, бавый",
                        end=True,
                    )
                )

        api.otherwise(start_next_story)

    return dialog
