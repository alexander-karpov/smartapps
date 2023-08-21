from functools import lru_cache
from dialoger import Dialog, TextReply, DialogAPI
from stories.AtLessonStory import AtLessonStory
from stories.CourtOfLawStory import CourtOfLawStory
from stories.InZooStory import InZooStory
from stories.ProverbsStory import ProverbsStory
from stories.story import Story


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    """
    Создаёт новый диалог «Самые смешные истории»
    """
    dialog = Dialog(stopwords=["алиса"])
    api = DialogAPI(dialog)

    stories: list[Story] = [
        InZooStory(api),
        CourtOfLawStory(api),
        ProverbsStory(api),
        AtLessonStory(api),
    ]

    @api.otherwise
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
