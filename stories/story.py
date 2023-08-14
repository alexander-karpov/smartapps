"""
Базовый класс историй
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine
from dialoger import DialogAPI
from entity_parser import Entity

StoryStep = Callable[[], None]


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
        Создаёт список шагов истории и начинает двигаться по ним
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
        Переход к следующему шагу. Если текущий шаг выполнен успешно
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
                    api.say(
                        "Я услышала что-то не то. Повтори, пожалуйста.",
                    )

                    self._repeat_current_step()

        return step

    def make_entity_step(self, questions: str | None, action: Callable[[Entity], None]):
        """
        Создаёт шаблонный шаг истории, ожидающий на вход сущность
        """
        api = self._api

        async def entity_action() -> bool:
            entities = api.input().entities()

            if entities:
                action(entities[0])

                return True

            return False

        return self.make_step(questions, entity_action)
