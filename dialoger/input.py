from typing import Any
from entity_parser import Entity, parse_entities


class Input:
    _request: dict[Any, Any]
    _entities: list[Entity] | None

    def __init__(self, request: dict[Any, Any]):
        self._request = request
        self._entities = None

    @property
    def is_new_session(self) -> bool:
        return self._request["session"]["new"]

    @property
    def tokens(self) -> list[str]:
        return self._request["request"]["nlu"]["tokens"]

    @property
    def utterance(self) -> str:
        return self._request["request"]["command"]

    @property
    def is_ping(self) -> bool:
        return "ping" in self.utterance

    @property
    def number(self) -> float | None:
        return next(
            (
                float(e["value"])
                for e in self._request["request"]["nlu"]["entities"]
                if e["type"] == "YANDEX.NUMBER"
            ),
            None,
        )

    @property
    def first_name(self) -> str | None:
        return next(
            (
                str(e["value"]["first_name"])
                for e in self._request["request"]["nlu"]["entities"]
                if e["type"] == "YANDEX.FIO" and "first_name" in e["value"]
            ),
            None,
        )

    @property
    def last_name(self) -> str | None:
        return next(
            (
                str(e["value"]["last_name"])
                for e in self._request["request"]["nlu"]["entities"]
                if e["type"] == "YANDEX.FIO" and "last_name" in e["value"]
            ),
            None,
        )

    def entities(self) -> list[Entity]:
        if self._entities is None:
            self._entities = parse_entities(self.utterance)

        return self._entities
