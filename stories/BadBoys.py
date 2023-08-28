"""
Однажды мама приходит домой и видит, что её маленькая дочка Верочка плачет.
- Верочка, почему ты плачешь? Что случилось? - с любопытством спрашивает мама.
- Мальчишки во дворе обижают меня и все время кричат "рога, рога"! - вскричала девочка.
- Не расстраивайся, дочка. Ишь ты, такая умница и красивая, не обращай на них внимания, просто игнорируй, и у них пройдет интерес. - успокаивает мама.

На следующий день мама опять встречает Верочку плачущей.
- Ой, Верочка, опять "рога" кричали? - спрашивает мама.
- Да... - отвечает девочка.
- И что ты сделала? - интересуется мама.
- Я их послушала, пока все начинали смеяться, а потом, когда развернулись, чтобы уйти, стукнула каждого палкой по рогам, - отвечает Верочка ушиваясь поглаживать свою палку.
- Ну что ж, отлично справилась! Теперь точно не будут обижать, - одобрительно улыбается мама.

Context: [ p:1576 c:420 t:1996 ]

© ChatGPT-4.0
"""


from dialoger import TextReply, Voice
from enrichment import add_random_adjective
from morphy import inflect
from stories.story import Story, StoryStep


class BadBoys(Story):
    """
    История про вредных мальчишек
    """

    _item: str

    def create_story_steps(self) -> list[StoryStep]:
        return [
            self.make_entity_step(
                "Назови любую часть тела.",
                lambda i: setattr(self, "_item", i.subject[0]),
            ),
            self._tell_story,
        ]

    async def _tell_story(self):
        api = self._api
        item = self._item
        item_ablt_plur = inflect(item, ["ablt", "plur"])
        item_adj_nomn_plur = await add_random_adjective(item, "nomn", "plur")

        if " " in item_adj_nomn_plur:
            [adj, noun] = item_adj_nomn_plur.split(" ")
            item_adj_nomn_plur = f"{noun} {adj}"

        api.say(
            "Однажды мама приходит домой и видит, что её маленькая дочка Верочка плачет. Мама спрашивает:",
            "- Верочка, почему ты плачешь? Что случилось?",
            "Девочка отвечает:",
            f"- Мальчишки во дворе обижают меня и все время кричат «{item}, {item}»!",
            "Мама её успокаивает:",
            "- Не расстраивайся, дочка. Ты такая умница и красавица, не обращай на них внимания и у них пропадёт интерес.",
            "",
            TextReply(
                f"- Противные мальчишки. Разве можно {item_ablt_plur} обзываться?",
                voice=Voice.ZAHAR_GPU,
            ),
            f"- Да! Сами они {item_adj_nomn_plur}. Рассказать, что было дальше?",
        )

        @api.otherwise
        async def _():
            item_datv = inflect(item, ["datv"])

            api.say(
                "На следующий день мама опять встречает Верочку плачущей. И говорит:",
                f"- Ой, Верочка, они опять кричали «{item}»?",
                "- Да... - отвечает девочка.",
                "- И что ты сделала? - спрашивает мама.",
                f"- Я их послушала, пока они смеялись, а когда развернулись чтобы уйти, я стукнула каждого палкой по {item_datv}.",
                "- отвечает Верочка и убирает свою палку.",
                "Мама вздохнула и сказала:",
                "- Ну что же... Теперь точно не будут обижать.",
                "",
                TextReply(
                    "- Надеюсь, мальчишки перестали дразнить Верочку?",
                    voice=Voice.ZAHAR_GPU,
                ),
                "- Да. После этого мы сразу подружились.",
            )

            await self.goto_next_step()
