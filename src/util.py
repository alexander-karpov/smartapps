from typing import Sequence
from yargy import Parser, rule # type: ignore
from yargy.pipelines import morph_pipeline # type: ignore


def cut_morph(command: str, words: Sequence[str]) -> str:
    """
    Удаляет совпадения в любой форме
    """
    pattern = rule(morph_pipeline(words))
    parser = Parser(pattern)

    result = []
    start = 0

    for m in parser.findall(command):
        part = command[start:m.span.start]

        if part:
            result.append(part.strip())

        start = m.span.stop + 1

    if start < len(command):
        result.append(command[start:])

    return " ".join(result)
