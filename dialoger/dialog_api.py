from dialoger.dialog import Dialog
from dialoger.handler import (
    IntentHandler,
    OtherwiseHandler,
    PostrollHandler,
    TriggerHandler,
)
from dialoger.input import Input
from dialoger.reply import Reply, TextReply
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar("T")
Action = Callable[[], Coroutine[Any, Any, None] | None]


class DialogAPI:
    """
    API над Dialog для построения обработчиков и ответов
    """

    _dialog: Dialog

    def __init__(self, dialog: Dialog) -> None:
        self._dialog = dialog

    def intent(
        self,
        *intent: str,
        include_yes: bool = False,
        include_no: bool = False,
        time_to_live=1,
    ):
        """
        Обработчик запроса по смыслу. Проверяются после trigger
        """

        def decorator(action: Action):
            phrases = intent

            if include_yes:
                phrases = phrases + (
                    "дальше",
                    # ---
                    "да",
                    "давай",
                    "хочу",
                    "буду",
                    "хорошо",
                    "согласен",
                    "конечно",
                    "безусловно",
                    "с удовольствием",
                    "поступим так",
                    "окей",
                    "пожалуй, да",
                    "разумеется",
                    "поддерживаю",
                    "идёт",
                    "принимаю",
                )

            if include_no:
                phrases = phrases + (
                    "нет",
                    "не надо",
                    "не хочу",
                    "не буду",
                    "не согласен",
                    "отказываюсь",
                    "не могу",
                    "никак нет",
                    "не подходит",
                    "извините, но нет",
                    "иеинтересно",
                    "ни в коем случае",
                    "Не собираюсь",
                    "отрицаю",
                    "не думаю",
                    "это не для меня",
                    "не вижу смысла",
                    "против",
                    "не сегодня",
                    "в другой раз",
                    "хватит",
                )

            self._dialog.append_handler(
                IntentHandler(
                    phrases=phrases,
                    action=action,
                    time_to_live=time_to_live,
                )
            )

            return action

        return decorator

    def trigger(self, trigger: Callable[[Input], T | None], time_to_live=1):
        """
        Обработчик запроса по условию. Проверяются первыми
        """

        def decorator(action: Callable[[T], Coroutine[Any, Any, None] | None]):
            self._dialog.append_handler(
                TriggerHandler(
                    trigger=trigger,
                    action=action,
                    time_to_live=time_to_live,
                )
            )

            return action

        return decorator

    def otherwise(self, action: Action):
        """
        Обработчик всех запросов, если они ещё не были обработаны
        """
        self._dialog.append_handler(
            OtherwiseHandler(
                action=action,
                time_to_live=1,
            )
        )

        return action

    def otherwise_always(self, action: Action):
        """
        Обработчик всех запросов, если они ещё не были обработаны
        """
        self._dialog.append_handler(
            OtherwiseHandler(
                action=action,
                time_to_live=100500,
            )
        )

        return action

    def postroll(self, action: Action):
        """
        Постролл иногда добавляется в конце случайного ответа
        """
        self._dialog.append_handler(
            PostrollHandler(
                action=action,
                time_to_live=1,
            )
        )

        return action

    def help(self, action: Callable[[], Coroutine[Any, Any, None] | None]):
        """
        Добавляет обработчик команды Помощь
        """
        return self.trigger(lambda i: i.utterance == "помощь", time_to_live=100500)(
            lambda _: action()
        )

    def what_can_you_do(self, action: Callable[[], Coroutine[Any, Any, None] | None]):
        """
        Добавляет обработчик команды Что ты умеешь
        """
        return self.trigger(
            lambda i: i.utterance == "что ты умеешь", time_to_live=100500
        )(lambda _: action())

    def say(self, *replies: Reply | str | tuple[str, str]):
        """
        Добавляет ответ на запрос. Вызывается внутри обработчика
        """
        for reply in replies:
            match reply:
                case Reply():
                    self._dialog.append_reply(reply)
                case _:
                    self._dialog.append_reply(TextReply(reply))

    def input(self) -> Input:
        """
        Текущий запрос
        """
        return self._dialog.input()
