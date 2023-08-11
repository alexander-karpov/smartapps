from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Generic, Protocol, TypeVar
from dialoger.input import Input

T = TypeVar("T")


class Handler(Protocol):
    generation: int


@dataclass
class IntentHandler:
    generation: int
    action: Callable[[], Coroutine[Any, Any, None] | None]
    phrases: tuple[str, ...]


@dataclass
class TriggerHandler(Generic[T]):
    generation: int
    action: Callable[[T], Coroutine[Any, Any, None] | None]
    trigger: Callable[[Input], T | None]


@dataclass
class OtherwiseHandler:
    generation: int
    action: Callable[[], Coroutine[Any, Any, None] | None]
    pass


@dataclass
class PostrollHandler:
    generation: int
    action: Callable[[], Coroutine[Any, Any, None] | None]
    pass
