from typing import cast
from pymorphy2 import MorphAnalyzer as MorphAnalyzerBase  # type: ignore
from pymorphy2.analyzer import Parse as ParseBase  # type: ignore
from pymorphy2.tagset import OpencorporaTag as OpencorporaTagBase  # type: ignore

# PARTS_OF_SPEECH
# ---------------
# NOUN - имя существительное
# ADJF - имя прилагательное (полное)
# ADJS - имя прилагательное (краткое)
# COMP - компаратив
# VERB - глагол (личная форма)
# INFN - глагол (инфинитив)
# PRTF - причастие (полное)
# PRTS - причастие (краткое)
# GRND - деепричастие
# NUMR - числительное
# ADVB - наречие
# NPRO - местоимение-существительное
# PRED - предикатив
# PREP - предлог
# CONJ - союз
# PRCL - частица
# INTJ - междометие

# CASES
# -----
# nomn - именительный падеж
# gent - родительный падеж
# datv - дательный падеж
# accs - винительный падеж
# ablt - творительный падеж
# loct - предложный падеж
# voct - звательный падеж
# gen1 - первый родительный падеж
# gen2 - второй родительный (частичный) падеж
# acc2 - второй винительный падеж
# loc1 - первый предложный падеж
# loc2 - второй предложный (местный) падеж


# Type stubs
# ----------
class OpencorporaTag(OpencorporaTagBase):
    """
    @see https://pymorphy2.readthedocs.io/en/stable/user/guide.html#id4
    """

    POS: str  # Part of Speech, часть речи
    animacy: str  # одушевленность
    aspect: str  # вид: совершенный или несовершенный
    case: str  # падеж
    gender: str  # род (мужской, женский, средний)
    involvement: str  # включенность говорящего в действие
    mood: str  # наклонение (повелительное, изъявительное)
    number: str | None  # число (единственное, множественное)
    person: str  # лицо (1, 2, 3)
    tense: str  # время (настоящее, прошедшее, будущее)
    transitivity: str  # переходность (переходный, непереходный)
    voice: str  # залог (действительный, страдательный)


class Parse(ParseBase):
    word: str
    tag: OpencorporaTag

    def __init__(self):
        raise Exception("Этот класс нужен только для доопределения типов")

    def inflect(self, required_grammemes: set[str]) -> "Parse":
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


def inflect(word: str, grs_variants: tuple[set[str], ...]) -> str:
    parsed = parse(word)

    for grs in grs_variants:
        for p in parsed:
            inflected = p.inflect(grs)

            if inflected:
                return inflected.word

    return word


def to_nomn(word: str) -> str:
    """
    Приводит к именительному падежу
    """

    match inflect(word, ({"nomn"},)):
        case nomn, _:
            return nomn
        case _:
            return word


def get_tag(word: str) -> OpencorporaTag:
    """
    Возвращает OpencorporaTag слова
    """
    parsed = parse(word)

    return parsed[0].tag


def by_gender(word: str, base: str, masc: str, femn: str, neut: str) -> str:
    """
    Выбор согласованного по полу слова
    """
    match get_tag(word).gender:
        case "masc":
            return base + masc
        case "femn":
            return base + femn
        case "neut":
            return base + neut
        case _:
            return base + masc
