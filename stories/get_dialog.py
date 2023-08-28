from functools import lru_cache
from dialoger import Dialog, TextReply, DialogAPI, Voice
from stories.AtLessonStory import AtLessonStory
from stories.BadBoys import BadBoys
from stories.CourtOfLawStory import CourtOfLawStory
from stories.InZooStory import InZooStory
from stories.ProverbsStory import ProverbsStory
from stories.story import Story


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    """
    Создаёт новый диалог «Самые смешные истории»
    """
    dialog = Dialog(intents_stopwords=["алиса"], voice=Voice.SHITOVA_GPU)
    api = DialogAPI(dialog)

    async def end_current_story():
        stories.pop(0)

        if stories:
            api.say("Вот такая история.")
            api.say("Хочешь послушать ещё одну?")

            api.otherwise(start_next_story)
        else:
            api.say("На сегодня это все истории.", "Хочешь послушать их ещё раз?")

            @api.intent(include_yes=True)
            async def _():
                stories.extend(get_stories())
                await start_next_story()

            def _no():
                api.say(
                    TextReply("Тут и сказки конец. А кто слушал – молодец", end=True)
                )

            api.intent(include_no=True)(_no)
            api.otherwise(_no)

    def get_stories():
        return [
            InZooStory(api, end_current_story),
            BadBoys(api, end_current_story),
            CourtOfLawStory(api, end_current_story),
            ProverbsStory(api, end_current_story),
            AtLessonStory(api, end_current_story),
        ]

    stories: list[Story] = get_stories()

    @api.what_can_you_do
    async def _():
        api.say(
            "Эта игра называется «Самые смешные истории»",
            "В ней мы вместе сочиним много всего интересного.",
            "Для этого я буду задавать вопросы, а твои ответы добавлю в нужные места в тексте и прочитаю историю, которая у нас получится.",
        )

        if stories:
            api.say("Теперь давай играть.")

            await stories[0].call_current_step()

    @api.help
    async def _():
        api.say(
            "Чтобы играть, тебе нужно слушать мои вопросы и отвечать на них. Чтобы закончить игру, скажи «Хватит».",
        )

        if stories:
            api.say("Теперь давай играть.")

            await stories[0].call_current_step()

    @api.otherwise
    def _():
        api.say(
            "Хорошо. Я знаю много весёлых историй и все они – чистая правда. Хочешь, расскажу тебе что-нибудь?",
            "Я буду задавать тебе вопросы. Твои ответы помогут мне вспомнить что-то интересное.",
            "Начинаем?",
        )

        # 🔥 button дальше

        api.otherwise(start_next_story)

    async def start_next_story():
        story = stories[0]

        if story:
            await story.call_current_step()
        else:
            api.say(
                TextReply(
                    "Ой! Кажется, у меня молоко убежало! Мне пора. Пока, бавый",
                    end=True,
                )
            )

    # Debug API
    # ---------
    @api.trigger(lambda i: i.utterance == "last", time_to_live=100500)
    async def _(_):
        last = stories.pop()
        stories.clear()
        stories.append(last)
        await start_next_story()

    return dialog
