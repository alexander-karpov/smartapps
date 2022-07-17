from dataclasses import dataclass
from typing import Any, Callable, Coroutine
from dialoger.input import Input


@dataclass
class Handler:
    action: Callable[[], Coroutine[Any, Any, None]]
    generation: int


@dataclass
class IntentHandler(Handler):
    phrases: tuple[str, ...]


@dataclass
class TriggerHandler(Handler):
    trigger: Callable[[Input], bool]


@dataclass
class OtherwiseHandler(Handler):
    pass

@dataclass
class PromptHandler(Handler):
    pass
