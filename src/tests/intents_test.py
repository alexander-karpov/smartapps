import pytest
from intents import AgreeIntent


class TestAgreeIntent():
    @pytest.fixture(scope='function')
    def intent(self):
        yield AgreeIntent()

    @pytest.mark.parametrize("command", [
        "буду",
        "да",
        "хорошо",
        "я на всё согласен",
    ])
    def test_positive(self, intent, command):
        assert intent.match(command)
        assert intent.yes

    @pytest.mark.parametrize("command", [
        "не буду",
        "не знаю",
        "не умею",
        "нет",
    ])
    def test_negative(self, intent, command):
        assert intent.match(command)
        assert not intent.yes

    @pytest.mark.parametrize("command", [
        "помощь",
        "чайник",
        "повтори",
        "меня зовут саша мне пять лет",
    ])
    def test_unrecognized(self, intent, command):
        assert not intent.match(command)
