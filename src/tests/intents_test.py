import pytest
from intents import AgreeIntent, YouGuessedRightIntent


class TestAgreeIntent:
    @pytest.fixture(scope='function')
    def intent(self):
        yield AgreeIntent()

    @pytest.mark.parametrize("command", [
        "буду",
        "да",
        "хорошо",
        "я на всё согласен",
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


class TestYouGuessedRightIntent:
    @pytest.fixture(scope='function')
    def intent(self):
        yield YouGuessedRightIntent()

    @pytest.mark.parametrize("command", [
        "да",
        "верно",
        "угадал",
        "правильно",
    ])
    def test_positive(self, intent: YouGuessedRightIntent, command: str):
        assert intent.match(command)
        assert intent.right

    @pytest.mark.parametrize("command", [
        "нет",
        "не верно",
        "не угадал",
        "неправильно",
    ])
    def test_negative(self, intent: YouGuessedRightIntent, command: str):
        assert intent.match(command)
        assert not intent.right

    @pytest.mark.parametrize("command", [
        "помощь",
        "чайник",
        "повтори",
        "меня зовут саша мне пять лет",
    ])
    def test_unrecognized(self, intent: YouGuessedRightIntent, command: str):
        assert not intent.match(command)

    def test_cast_to_true(self, intent: YouGuessedRightIntent):
        intent.match('да')

        assert intent

    def test_cast_to_false(self, intent: YouGuessedRightIntent):
        intent.match('нет')

        assert not intent
