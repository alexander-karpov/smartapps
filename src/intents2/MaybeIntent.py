from typing import Any, Callable, Generic, TypeVar
from dialog import Intent

TIntent = TypeVar("TIntent", bound=Intent)

class MaybeIntent(Intent, Generic[TIntent]):
    _intent: TIntent
    _is_matched: bool

    def __init__(self, intent: TIntent) -> None:
        super().__init__()

        self._intent = intent


    def match(self, command: str) -> bool:
        self._is_matched = self._intent.match(command)

        return True

    def maybe(self, selector: Callable[[TIntent], Any]) -> Any:
        if not self._is_matched:
            return None

        return selector(self._intent)

    def __bool__(self) -> bool:
        return self._is_matched
