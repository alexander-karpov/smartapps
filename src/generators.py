from abc import ABC, abstractmethod
from typing import Iterator, List
from pymongo import MongoClient
import random


class BufferedSequence(ABC):
    _buffer: Iterator[str] = iter([])

    @abstractmethod
    def _get_next_batch() -> Iterator[str]:
        pass

    def __iter__(self):
        return self

    def __next__(self) -> str:
        try:
            return next(self._buffer)
        except StopIteration:
            self._buffer = self._get_next_batch()

        return next(self._buffer)


class ShuffledSequence(BufferedSequence):
    _items: List[str]

    def __init__(self, items: List[str]):
        super().__init__()

        self._items = items.copy()

    def _get_next_batch(self) -> Iterator[str]:
        random.shuffle(self._items)

        return iter(self._items)
