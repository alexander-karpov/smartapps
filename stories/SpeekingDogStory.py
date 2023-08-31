"""
Однажды трое детей, Маша, Вася и Сережа решили научить собаку говорить. За это мама обещала им купить велосипеды.
Устав от безуспешных попыток, дети отправились на улицу, чтобы подумать над проблемой и внезапно встретили дядю Васю – местного изобретателя.

Дядя Вася предложил детям свою новую разработку – специальный "переводчик" для собачьего лая. Маша, Вася и Сережа подключили устройство к своей собаке Бобику и были шокированы его "разговором".

- Привет, Маша, Вася и Сережа, - прозвучал голос спустя некоторое время. - Я знаю, что вы хотите научить меня говорить и получить велосипеды. 

Дети с восторгом побежали к маме и показали ей устройство и чудо-переводчик. Мама была настолько поражена, что сразу же купила им велосипеды. 

Когда мама вышла из магазина, Бобик улыбнулся и сказал детям, снова глядя на устройство: 
- Исполнено! Настало время снять мою маску лающего и вот этот глупый переводчик. Привет, меня зовут Орм, я из Роскосмоса, и я прилетел сюда, чтобы проучить ваших родителей, что осваивать навыки английского и других языков на деле, а не только мечтать об этом!

И все посмеялись, поймав мысль отсылки к обучению детей говорить на разных языках, научившись большому уроку от инопланетянина-собаки.

Context: [ p:6637 c:596 t:7233 ]

© ChatGPT-4.0
"""

from dialoger import TextReply, Voice
from enrichment import add_random_adjective
from morphy import by_gender, inflect, parse
from stories.story import Story, StoryStep


class SpeekingDogStory(Story):
    """
    История то как дети учили собаку говорить
    """

    _dog_word: str
    _gift: str
    _junk: str

    def create_story_steps(self) -> list[StoryStep]:
        return [
            self.make_step(
                "Назови хорошее слово.",
                self._save_dog_word,
            ),
            self.make_entity_step(
                "Что хочет в подарок любой ребёнок?",
                lambda i: setattr(self, "_gift", i.subject[0]),
            ),
            self.make_entity_step(
                "Что хочет в подарок любой взрослый?",
                lambda i: setattr(self, "_junk", i.subject[0]),
            ),
            self._tell_story,
        ]

    async def _save_dog_word(self) -> bool:
        self._dog_word = self._api.input().utterance

        return True

    async def _tell_story(self):
        api = self._api
        dog_word = self._dog_word
        gift = self._gift
        junk = self._junk

        gift_accs_plur = inflect(gift, ["accs", "plur"])
        gift_accs_sing = inflect(gift, ["accs", "sing"])

        gift_tag = parse(gift)[0].tag
        _new_plur = inflect(
            "новый", ["nomn", "plur", gift_tag.gender, gift_tag.animacy]
        )
        _new = inflect("новый", ["accs", gift_tag.gender, gift_tag.animacy])

        # junk_accs = inflect(junk, ["accs"])
        junk_adj_accs = await add_random_adjective(junk, "accs", "sing")

        junk_tag = parse(junk)[0].tag
        old = inflect("старый", ["accs", junk_tag.gender, junk_tag.animacy])
        needed = inflect("нужный", ["accs", junk_tag.gender, junk_tag.animacy])

        api.say(
            f"Однажды Маша и Серёжа решили научить свою собаку Бобика говорить. За это Мама обещала им купить {_new_plur} {gift_accs_plur}.",
            "Целый день они по-очереди твердили Бобику:",
            f"- Скажи - «{dog_word}». Скажи - «{dog_word}».",
            "Собака слушала их и веляла хвостом, но разговаривать не хотела.",
            "Устав от безуспешных попыток, дети отправились на улицу, чтобы подумать над проблемой и внезапно встретили дядю Васю – местного изобретателя.",
            "Дядя Вася предложил детям свою новую разработку – специальный переводчик для собачьего лая.",
            "",
            TextReply(
                "- Переводчик для собачьего лая? Этот дядя Вася – настоящий гений!",
                voice=Voice.ZAHAR_GPU,
            ),
            "- Да. И выдумщик. Рассказать, что было дальше?",
        )

        @api.otherwise
        async def _():
            api.say(
                f"Дядя Вася сказал, что согласен обменять переводчик на {junk_adj_accs}.",
                f"Маша и Серёжа обрадовались такой удаче и скорее побежали домой. Дома они нашли {old} не{needed} {junk} и обменяли {by_gender(junk, '', 'его','её','его')} на собачий переводчик.",
                "Они подключили его к Бобику и с восторгом побежали к Маме, чтобы показать ей как работает это чудо-устройство.",
                "Когда они прибежали, Бобик подошёл к Маме, посмотрел на неё грустными глазами и сказал:",
                "",
                f"– Мама, я тоже хочу {_new} {gift_accs_sing}.",
                "",
                f"Мама была настолько поражена, что сразу же купила им {gift_accs_plur}.",
                "",
                TextReply(
                    "- А я умею разговаривать по-собачьи. Гав-гав.",
                    voice=Voice.ZAHAR_GPU,
                ),
                "- Здорово! Хороший мальчик.",
            )

            await self.goto_next_step()
