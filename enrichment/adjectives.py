"""
Предоставляет прилагательные для существительных
"""

import random
import httpx
from async_lru import alru_cache
from morphy import inflect, parse

_client = httpx.AsyncClient()


async def add_random_adjective(
    noun: str, case: str | None = None, num: str | None = None
) -> str:
    """
    Добавляет к существительному случайное прилагательное,
    если сможет его согласовать
    """
    parsed_noun = parse(noun)[0]

    adjectives = await _upload_adjectives(parsed_noun.normal_form)

    if not adjectives:
        return noun

    num_ = num or parsed_noun.tag.number
    case_ = case or parsed_noun.tag.case
    # Пол не имеет значения во множественном сичле
    gender_ = parsed_noun.tag.gender if num_ != "plur" else None
    # Одушевленность имеет значение только в мужском роде
    anim_ = parsed_noun.tag.animacy if case_ == "masc" else None

    random_adjective = random.choice(adjectives)
    grs = [
        gr
        for gr in [
            num_,
            gender_,
            case_,
            anim_,
        ]
        if gr is not None
    ]

    return f"{inflect(random_adjective, grs)} {inflect(noun, grs)}"


@alru_cache(1024)
async def _upload_adjectives(word: str) -> tuple[str]:
    response = await _client.get(
        f"https://functions.yandexcloud.net/d4e24s0e8pnki6olgvgi?text={word}"
    )

    if response.status_code != 200:
        return tuple()

    # Пример текста: чай:английский чай:ароматный чай:бабушкин чай:белый
    return tuple(word.split(":")[1] for word in response.text.split())
