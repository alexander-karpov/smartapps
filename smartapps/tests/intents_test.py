from typing import Tuple
import pytest
from intents import AgreeIntent, EatableGuessIntent, EatablePuzzleIntent, YouGuessedRightIntent


class TestAgreeIntent:
    @pytest.fixture(scope='function')
    def intent(self):
        yield AgreeIntent()

    @pytest.mark.parametrize("command", [
        "да",
        "буду",
        "я умею",
        "хорошо",
        "я на всё согласен",
        "да я лучше тебя знаю",
    ])
    def test_positive(self, intent: AgreeIntent, command: str):
        assert intent.match(command)
        assert intent.yes

    @pytest.mark.parametrize("command", [
        "не буду",
        "не знаю",
        "не умею",
        "нет",
    ])
    def test_negative(self, intent: AgreeIntent, command: str):
        assert intent.match(command)
        assert not intent.yes

    @pytest.mark.parametrize("command", [
        "помощь",
        "чайник",
        "повтори",
        "меня зовут саша мне пять лет",
    ])
    def test_unrecognized(self, intent: AgreeIntent, command: str):
        assert not intent.match(command)

    def test_cast_to_true(self, intent: AgreeIntent):
        intent.match('да')

        assert intent

    def test_cast_to_false(self, intent: AgreeIntent):
        intent.match('нет')

        assert not intent


class TestYouGuessedRightIntent:
    @pytest.fixture(scope='function')
    def intent(self):
        yield YouGuessedRightIntent()

    @pytest.mark.parametrize("command", [
        "да",
        "верно",
        "угадал",
        "отгадала",
        "правильно",
    ])
    def test_positive(self, intent: YouGuessedRightIntent, command: str):
        assert intent.match(command)
        assert intent.right
        assert not intent.wrong

    @pytest.mark.parametrize("command", [
        "нет",
        "неа",
        "не верно",
        "не угадал",
        "неправильно",
    ])
    def test_negative(self, intent: YouGuessedRightIntent, command: str):
        assert intent.match(command)
        assert intent.wrong
        assert not intent.right

    @pytest.mark.parametrize("command", [
        "помощь",
        "чайник",
        "повтори",
        "меня зовут саша мне пять лет",
    ])
    def test_unrecognized(self, intent: YouGuessedRightIntent, command: str):
        assert intent.match(command)
        assert not intent.right
        assert not intent.wrong

    def test_cast_to_bool(self, intent: YouGuessedRightIntent):
        intent.match('да')

        with pytest.raises(NotImplementedError):
            bool(intent)


class TestEatableRiddleIntent:
    @pytest.fixture(scope='function')
    def intent(self):
        yield EatablePuzzleIntent()

    @pytest.mark.parametrize("cases", [
        ("банан это съедобно", "банан"),
        ("шампунь для волос это вкусно или не вкусно", "шампунь для волос"),
        ("зубную щетку можно есть", "зубную щетку"),
        ("зубная паста это съедобное или несъедобное", "зубная паста"),
        ("алиса сок это съедобное", "сок"),
    ])
    def test_positive(self, intent: EatablePuzzleIntent, cases: Tuple[str, str]):
        assert intent.match(cases[0])
        assert intent.riddle == cases[1]


class TestEatableGuessIntent:
    @pytest.fixture(scope='function')
    def intent(self):
        yield EatableGuessIntent()

    @pytest.mark.parametrize("command", [
        "не знаю",
    ])
    def test_dont_know(self, intent: EatableGuessIntent, command: str):
        assert intent.match(command)
        assert intent.dont_know
