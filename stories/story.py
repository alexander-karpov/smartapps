from abc import ABC, abstractmethod
from random import choice
from typing import Any, Callable, Coroutine
from dialoger import DialogAPI

StoryStep = Callable[[], None]

PLEASE_REPEAT = [
    "Ой! Я немного отвлеклась. Что ты говоришь?",
    "Это так необычно. Повтори, пожалуйста.",
]


class Story(ABC):
    """
    Базовый класс историй
    """

    _steps: list[StoryStep]
    _api: DialogAPI

    def __init__(self, api: DialogAPI) -> None:
        self._api = api
        self._steps = []

    @abstractmethod
    def create_steps(self) -> list[StoryStep]:
        """
        Формирует список шагов истории
        """

    def start(self, last_step: StoryStep) -> None:
        """
        Создаёт списог шагов истории и начинает двигаться по ним
        """
        self._steps = self.create_steps()
        self._steps.append(last_step)

        self._steps[0]()

    def _repeat_current_step(self) -> None:
        """
        (Повторно) заходит в текущий (пройденный) шаг истории
        """
        self._steps[0]()

    def goto_next_step(self) -> None:
        """
        (Повторно) заходит в текущий (пройденный) шаг истории
        """
        self._steps.pop(0)
        self._steps[0]()

    def make_step(
        self,
        questions: str | None,
        action: Callable[[], Coroutine[Any, Any, bool]],
    ):
        """
        Создаёт шаблонный шаг истории
        """
        api = self._api

        def step() -> None:
            if questions:
                api.say(questions)

            @api.otherwise
            async def _():
                if await action():
                    self.goto_next_step()

                else:
                    api.say(choice(PLEASE_REPEAT))

                    self._repeat_current_step()

        return step
