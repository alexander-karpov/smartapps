from typing import Sequence
from yargy import Parser, rule # type: ignore
from yargy.pipelines import morph_pipeline # type: ignore


def cut_morph(command: str, words: Sequence[str]) -> str:
    """
    Удаляет совпадения в любой форме
    """
    pattern = rule(morph_pipeline(words))
    parser = Parser(pattern)

    match = parser.find(command) # type: ignore

    if match is None:
        return command

    return command[:match.span.start] + command[match.span.stop:] # type: ignore
