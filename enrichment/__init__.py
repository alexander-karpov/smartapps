from random import choice
import httpx
from morphy import inflect, parse
from async_lru import alru_cache

_client = httpx.AsyncClient()


async def add_random_adjective(noun: str) -> str:
    """
    Добавляет к существительному случайное прилагательное,
    если сможет его согласовать
    """
    parsed_noun = parse(noun)[0]

    adjectives = await _upload_adjectives(parsed_noun.normal_form)

    if not adjectives:
        return noun

    random_adjective = choice(adjectives)

    in_same_case = inflect(
        random_adjective,
        (
            {parsed_noun.tag.case, parsed_noun.tag.gender, parsed_noun.tag.number},
            {parsed_noun.tag.case, parsed_noun.tag.gender},
            {parsed_noun.tag.case, parsed_noun.tag.number},
            {parsed_noun.tag.case},
        ),
    )

    if not in_same_case:
        return noun

    case_consistent_adjective, _ = in_same_case

    return f"{case_consistent_adjective} {noun}"


@alru_cache(1024)
async def _upload_adjectives(word: str) -> tuple[str]:
    response = await _client.get(
        f"https://functions.yandexcloud.net/d4e24s0e8pnki6olgvgi?text={word}"
    )

    if response.status_code != 200:
        return tuple()

    # Пример текста: чай:английский чай:ароматный чай:бабушкин чай:белый
    return tuple(word.split(":")[1] for word in response.text.split())
