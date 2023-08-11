"""
Специфичная для entity_parser работа с pymorphy
"""
from typing import Set, List, Tuple
from morphy import OpencorporaTag, Parse, parse


def _sort_morphemes(morphemes: List[Parse]) -> List[Parse]:
    """
    Отдаём предпочтение некоторым формам
    """

    _sorted = sorted(
        morphemes,
        key=lambda m: [
            # Тут формируется вектор типа [false, true, false] где false поднимается вверх
            "inan" in m.tag,
            "sing" not in m.tag,
            "nomn" not in m.tag,
        ],
    )

    # Отсекаем глагоды: чернила – это краска, а не глагол жен.
    return [m for m in _sorted if "VERB" not in m.tag]


def inflect(word: str, grs_variants: List[Set[str]]) -> Tuple[str, OpencorporaTag]:
    """
    Привотид слово в нужную форму. Специфика поиска сущностей
    """
    parsed = _sort_morphemes(parse(word))

    for grs in grs_variants:
        for p in parsed:
            inflected = p.inflect(grs)

            if inflected:
                return (inflected.word, inflected.tag)

    raise KeyError(f"Не найдено склонение {grs_variants} для слова {word}")


def get_tag(word: str) -> OpencorporaTag:
    """
    Возвращает OpencorporaTag слова
    """
    parsed = _sort_morphemes(parse(word))

    return parsed[0].tag
