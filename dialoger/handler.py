from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Generic, Protocol, TypeVar
from dialoger.input import Input

T = TypeVar("T")


class Handler(Protocol):
    time_to_live: int


@dataclass
class IntentHandler:
    time_to_live: int
    action: Callable[[], Coroutine[Any, Any, None] | None]
    phrases: tuple[str, ...]


@dataclass
class TriggerHandler(Generic[T]):
    time_to_live: int
    action: Callable[[T], Coroutine[Any, Any, None] | None]
    trigger: Callable[[Input], T | None]


@dataclass
class OtherwiseHandler:
    time_to_live: int
    action: Callable[[], Coroutine[Any, Any, None] | None]
    pass


@dataclass
class PostrollHandler:
    time_to_live: int
    action: Callable[[], Coroutine[Any, Any, None] | None]
    pass
