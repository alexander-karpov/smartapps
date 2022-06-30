
from dataclasses import dataclass
from typing import Callable
from dialoger.input import Input


@dataclass
class Handler:
    action: Callable[[], None]
    generation: int


@dataclass
class PhraseHandler(Handler):
    phrases: tuple[str, ...]


@dataclass
class TriggerHandler(Handler):
    trigger: Callable[[Input], bool]


@dataclass
class OtherwiseHandler(Handler):
    pass