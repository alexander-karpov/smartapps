from typing import ClassVar
from util import cut_morph
from enum import Enum, auto
from smartapps.dialog.dialog import Intent
from yargy import Parser, rule, or_ # type: ignore
from yargy.predicates import eq, gram, true # type: ignore
from yargy.pipelines import morph_pipeline


class NounIntent(Intent):
    _parser: ClassVar[Parser] = Parser(rule(gram('NOUN')))
    noun: str

    def match(self, command: str) -> bool:
        try:
            self.noun = next(match.tokens[0].value
                        for match in NounIntent._parser.findall(command)
                        # Отсекаем короткие слова, которые подходят по любые условия
                        if len(match.tokens[0].value) >= 3)

            return True
        except StopIteration:
            return False


class EatablePuzzleIntent(Intent):
    riddle: str

    def match(self, command: str) -> bool:
        if not NounIntent().match(command):
            return False

        self.riddle = cut_morph(command)

        return True


class IKnow(Intent):
    yes: bool
    _dont_know_parser: ClassVar[Parser] = Parser(rule(eq("не"), morph_pipeline(["знаю"])))
    _know_parser: ClassVar[Parser] = Parser(morph_pipeline(["знаю"]))

    def __init__(self) -> None:
        super().__init__()

        self.yes = False

    def match(self, command: str) -> bool:
        if IKnow._dont_know_parser.find(command):
            return True

        if IKnow._know_parser.find(command):
            self.yes = True

            return True

        return False


CAN = morph_pipeline([
        "да",
        "буду",
        "знаю",
        "умею",
        "могу",
        "хочу",
        "играл",
        "готов",
        "хорошо",
        "понимаю",
        "конечно",
        "согласен",
        "попробую",
        "справлюсь",
        "лучше тебя",
    ])

NO = rule(eq("нет"))

CANNOT = rule(
    or_(eq("не"), eq('плохо')),
    true().optional(),
    true().optional(),
    CAN
)

class AgreeIntent(Intent):
    yes: bool = False
    _cannot_parser: ClassVar[Parser] = Parser(or_(NO, CANNOT))
    _can_parser: ClassVar[Parser] = Parser(CAN)

    def match(self, command: str) -> bool:


        if AgreeIntent._cannot_parser.find(command):
            return True

        if AgreeIntent._can_parser.find(command):
            self.yes = True

            return True

        return False

    def __bool__(self) -> bool:
        return self.yes

EATABLE = morph_pipeline([
    "вкуснятина",
    "вкуснотища",
    "объеденье",
    "съедобное",
    "конечно",
    "вкусно",
    "кушать",
    "обожаю",
    "сладко",
    "люблю",
    "можно",
    "ням",
    "ем",
    "ам",
    "да",
])

UNEATABLE = or_(
    morph_pipeline([
        "отвратительно",
        "несъедобное",
        "невкусно",
        "гадость",
        "ужасно",
        "нельзя",
        "нет",
        "бя",
        "бе",
        "фу",
    ]),
    rule(
        or_(eq("не"), eq('нельзя')),
        true().optional(),
        true().optional(),
        EATABLE
    ),
    rule(
        EATABLE,
        true().optional(),
        or_(eq("не"), eq('нельзя'))
    )
)

class EatableGuessIntent(Intent):
    class Guess(Enum):
        EATABLE = auto()
        UNEATABLE = auto()
        DONT_KNOW = auto()

    is_uneatable: bool = False
    is_eatable: bool = False
    dont_know: bool = False

    _uneatable_parser: ClassVar[Parser] = Parser(UNEATABLE)
    _eatable_parser: ClassVar[Parser] = Parser(EATABLE)

    def match(self, command: str) -> bool:
        i_know = IKnow()

        if i_know.match(command) and not i_know.yes:
            self.dont_know = True

            return True

        if EatableGuessIntent._uneatable_parser.find(command):
            self.is_uneatable = True

            return True

        if EatableGuessIntent._eatable_parser.find(command):
            self.is_eatable  = True

            return True

        return False


YES = rule(eq("да"))
NO = rule(eq("нет"))
NOU = rule(eq("неа"))
RIGHT = morph_pipeline(["правильно", "угадал", "отгадал", "верно", "точно", "выиграл"])
NOT_RIGHT = rule(or_(eq("не")), RIGHT)
WRONG = morph_pipeline(["неправильно", "неверно", "ошибся", "проиграл"])


right_parser = Parser(or_(RIGHT, YES))
not_right_parser = Parser(or_(NOT_RIGHT, NO, NOU, WRONG))


class YouGuessedRightIntent(Intent):
    right: bool = False
    wrong: bool = False

    def match(self, command: str) -> bool:
        if not_right_parser.find(command):
            self.wrong = True

        elif right_parser.find(command):
            self.right = True

        return True

    def __bool__(self) -> bool:
        raise NotImplementedError()


class WhatCanYouDoIntent(Intent):
    def match(self, command: str) -> bool:
        return "что ты умеешь" in command
