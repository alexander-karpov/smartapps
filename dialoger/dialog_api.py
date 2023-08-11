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
    ):
        """
        Обработчик запроса по смыслу. Проверяются после trigger
        """

        def decorator(action: Action):
            phrases = intent

            if include_yes:
                phrases = phrases + (
                    "да",
                    "давай",
                    "хочу",
                    "буду",
                    "хорошо",
                    "согласен",
                )

            self._dialog.append_handler(
                IntentHandler(
                    phrases=phrases,
                    action=action,
                    time_to_live=1,
                )
            )

            return action

        return decorator

    def trigger(
        self,
        trigger: Callable[[Input], T | None],
    ):
        """
        Обработчик запроса по условию. Проверяются первыми
        """

        def decorator(action: Callable[[T], Coroutine[Any, Any, None] | None]):
            self._dialog.append_handler(
                TriggerHandler(
                    trigger=trigger,
                    action=action,
                    time_to_live=1,
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

    def new_session(self, action: Action):
        """
        Обработчик первого запрос
        """
        self._dialog.append_handler(
            TriggerHandler(
                trigger=lambda i: i.is_new_session,
                action=lambda _: action(),
                time_to_live=1,
            )
        )

        return action

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
