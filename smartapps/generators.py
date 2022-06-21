from abc import ABC, abstractmethod
from typing import Generic, Iterator, List, Sequence, TypeVar
from pymongo import MongoClient
import random

ТItem = TypeVar("ТItem")


class BufferedSequence(ABC, Generic[ТItem]):
    _buffer: Iterator[ТItem] = iter([])

    @abstractmethod
    def _get_next_batch() -> Iterator[ТItem]:
        pass

    def __iter__(self):
        return self

    def __next__(self) -> ТItem:
        try:
            return next(self._buffer)
        except StopIteration:
            self._buffer = self._get_next_batch()

        return next(self._buffer)


class ShuffledSequence(BufferedSequence[ТItem]):
    _items: List[ТItem]

    def __init__(self, items: Sequence[ТItem]):
        super().__init__()

        self._items = list(items)

    def _get_next_batch(self) -> Iterator[ТItem]:
        random.shuffle(self._items)

        return iter(self._items)
