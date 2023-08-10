from typing import Optional, cast
from pymorphy2 import MorphAnalyzer as MorphAnalyzerBase  # type: ignore
from pymorphy2.analyzer import Parse as ParseBase  # type: ignore
from pymorphy2.tagset import OpencorporaTag  # type: ignore


# Type stubs
# ----------
class Parse(ParseBase):
    word: str
    tag: OpencorporaTag

    def __init__(self):
        raise Exception("Этот класс нужен только для доопределения типов")

    def inflect(self, required_grammemes: frozenset[str]) -> "Parse":
        ...


class MorphAnalyzer(MorphAnalyzerBase):
    def __init__(self):
        raise Exception("Этот класс нужен только для доопределения типов")

    def parse(self, word: str) -> list[Parse]:
        ...


# Implementation
# --------------

_morph = cast(MorphAnalyzer, MorphAnalyzerBase())


def parse(word: str) -> list[Parse]:
    return _morph.parse(word)


def inflect(
    word: str, grs_variants: tuple[frozenset[str], ...]
) -> Optional[tuple[str, OpencorporaTag]]:
    parsed = parse(word)

    for grs in grs_variants:
        for p in parsed:
            inflected = p.inflect(grs)

            if inflected:
                return (inflected.word, inflected.tag)

    return None
