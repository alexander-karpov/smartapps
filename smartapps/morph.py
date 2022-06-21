from typing import Set
import pymorphy2
# from functools import lru_cache

morph = pymorphy2.MorphAnalyzer()

# @lru_cache(128)
def inflect(word: str, grs: Set[str]) -> str:
    for parsed in morph.parse(word):
        inflected = parsed.inflect(grs)

        if inflected:
            return inflected.word

    raise Exception(f"Не найдено склонение {grs} для слова {word}")

def get_tag(word: str):
    return morph.parse(word)[0].tag
