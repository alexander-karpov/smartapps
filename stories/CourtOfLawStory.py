from dialoger import TextReply, Voice
from enrichment.adjectives import add_random_adjective
from morphy import inflect
from stories.story import Story, StoryStep


class CourtOfLawStory(Story):
    """
    В одной семье живут маленькие дети – Вовочка и Машенька. Однажды они решают сыграть в суд. Играть-то надо кому-то быть судьей, а кому-то ответчиком, поэтому Машенька предлагает:
    — Вовочка, давай у меня будут спрашивать, а я буду отвечать!
    Вовочка соглашается, и они начинают:
    — Машенька, почему ты укусила бабушку за палец?
    — Я ее запутала с колбасой.
    — А почему ты потом упала с кровати?
    — Хотела стать бруквой "О"!
    — И почему ты полилась слезами и весь день хныкала?
    — Я без зарядки!
    Вовочка хмурится и произносит строго:
    — Приговор является непосредственным - пойдем объясним все папе. Теперь он точно поймет детскую логику!
    """

    _food: str
    _item: str
    _power: str

    def create_story_steps(self) -> list[StoryStep]:
        return [
            self.make_entity_step(
                "Назови что-то съедобное.",
                lambda i: setattr(self, "_food", i.subject[0]),
            ),
            self.make_entity_step(
                "Назови любой предмет рядом с тобой.",
                lambda i: setattr(self, "_item", i.subject[0]),
            ),
            self.make_entity_step(
                "Что придаёт сил и поднимает настроение?",
                lambda i: setattr(self, "_power", i.subject[0]),
            ),
            self._tell_story,
        ]

    async def _tell_story(self) -> None:
        food_ablt = inflect(self._food, ["ablt"])
        food_adj_ablt = await add_random_adjective(self._food, "ablt")
        item_ablt = inflect(self._item, ["ablt"])
        power_gent = inflect(self._power, ["gent"])

        self._api.say(
            "В одной семье жили маленькие брат и сестра – Вовочка и Машенька.",
            "Однажды они решают сыграть в суд. Кому-то надо быть судьей, а кому-то ответчиком, поэтому Машенька предлагает:",
            "— Вовочка, давай у меня будут спрашивать, а я буду отвечать!",
            "Вовочка соглашается, и они начинают играть. Вовочка спрашивает:",
            "— Машенька, почему ты укусила бабушку за палец?",
            "Маша отвечает:",
            f"— Я её перепутала с {food_adj_ablt}.",
            "Вовочка продолжает:",
            "— А почему ты потом упала с кровати?",
            "Маша в ответ:",
            f" — Я хотела стать {item_ablt}!",
            "",
            TextReply(
                f"- В детстве я тоже хотел стать {item_ablt}.", voice=Voice.ZAHAR_GPU
            ),
            "- Получилось?",
            TextReply("- Не совсем.", voice=Voice.ZAHAR_GPU),
            "- А у меня получилось. Рассказать, что было дальше?",
        )

        @self._api.otherwise
        async def _():
            self._api.say(
                "Вовочка спрашивает дальше:",
                " — И почему ты облил+ась слезами и весь день хныкала?",
                "На это Машенька отвечает:",
                f"— Я сегодня без {power_gent}!",
                "Вовочка хмурится и произносит строго:",
                "— Приговор является окончательным - пойдем объясним все папе. Теперь он точно поймет детскую логику!",
                "",
                TextReply(
                    "- Вот так Вовочка. Пусть простит Машеньку.",
                    voice=Voice.ZAHAR_GPU,
                ),
                f"- Да. Подумаешь, бабушку с {food_ablt} перепутала. У всех так бывает.",
                "Правда ведь?",
            )

            await self.goto_next_step()
