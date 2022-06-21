from typing import Sequence
from yargy import Parser, rule # type: ignore
from yargy.pipelines import morph_pipeline # type: ignore


_parser = Parser(rule(morph_pipeline([
    "это",
    "или",
    "алиса",
    'вкусное',
    'невкусное',
    'не вкусное',
    "можно есть",
    'съедобное',
    'несъедобное',
    'не съедобное',
])))


def cut_morph(command: str) -> str:
    """
    Удаляет совпадения в любой форме
    """

    result = []
    start = 0

    for m in _parser.findall(command):
        part = command[start:m.span.start]

        if part:
            result.append(part.strip())

        start = m.span.stop + 1

    if start < len(command):
        result.append(command[start:])

    return " ".join(result)
