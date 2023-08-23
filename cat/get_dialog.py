from functools import lru_cache
import re
from cat.append_chitchat import append_chitchat
from dialoger import Dialog, DialogAPI, Voice, TextReply


class CatDialogAPI(DialogAPI):
    catlang = {"мя": "мяу", "ня": "няу", "му": "мур"}
    pattern = r"(мя|ня|му)([^а-я|А-Я]|$)"

    def cat_say(self, *replies: str):
        """
        Перед добавлением в ответ, добавляет в текст мяукание
        """
        catlang = CatDialogAPI.catlang
        pattern = CatDialogAPI.pattern

        for reply in replies:
            self._dialog.append_reply(
                TextReply(
                    (
                        re.sub(
                            pattern,
                            lambda m: f"{catlang.get(m.group(1), m.group(1))} "
                            if catlang.get(m.group(1))
                            else m.group(0),
                            reply,
                        ),
                        re.sub(
                            pattern,
                            lambda m: f"{catlang.get(m.group(1), m.group(1))}- "
                            if catlang.get(m.group(1))
                            else m.group(0),
                            reply,
                        ),
                    )
                )
            )


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(default_voice=Voice.SASHA_GPU)
    api = CatDialogAPI(dialog)

    @api.otherwise
    def _():
        api.say(
            TextReply(
                "Привет. Знаешь, кто тут живёт? Это мой друг – котёнок.",
                "Хочешь с ним познакомиться?",
                "Я неплохо знаю кошачий язык и буду переводить.",
                "Запомни главное правило кошачьего языка:",
                "если не знаешь, что сказать, скажи «мяу».",
                "Готов попробовать?",
                voice=Voice.SHITOVA_GPU,
            )
        )

        append_wait_meow()

    def append_wait_meow():
        @api.trigger(lambda i: "мяу" in i.tokens)
        def _(_):
            api.cat_say("Мяу.", "Кто здесь?")

            append_chitchat(api)

        @api.otherwise
        def _():
            api.say(
                TextReply(
                    "Нужно сказать не",
                    f"«{api.input().utterance}»",
                    ", а «мяу».",
                    voice=Voice.SHITOVA_GPU,
                )
            )

            append_wait_meow()

    return dialog
