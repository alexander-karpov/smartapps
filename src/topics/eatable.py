from intents import EatableRiddleIntent, AgreeIntent, EatableGuessIntent, WhatCanYouDoIntent, YouGuessedRightIntent
from loggers import RiddleLogger
from dialog import HelpReply, TextReply, Topic
from generators import ShuffledSequence
from services import EatableClassifierService, EatableRiddleService


USER_RIGHT_TEXT = [
    'Верно.',
    'Правильно.',
    'Правильно. Молодец.',
    'Верно. Молодец.',
    'Ты угадал.',
    'Верно. Ты угадал.',
]

USER_RIGHT_EATABLE_TEXT = [
    *USER_RIGHT_TEXT,
    "Да.",
    'Я однажды скушала это. Правильно.',
    'Ням-ням. Правильно.',
    'Ам! Я скушала.',
]

USER_RIGHT_UNEATABLE_TEXT = [
    *USER_RIGHT_TEXT,
    'Фу! Не скушать. Правильно.',
    'Верно. Это не для животика.',
    'Правильно. Такое есть нельзя.'
]


class EatableTopic(Topic, EatableClassifierService, EatableRiddleService):
    def __init__(
        self,
        riddle_logger: RiddleLogger
    ) -> None:
        super().__init__()

        self._riddle_logger = riddle_logger

    def flow(self) -> Topic.Flow:
        user_right_eatable_text = ShuffledSequence(USER_RIGHT_EATABLE_TEXT)
        user_right_uneatable_text = ShuffledSequence(USER_RIGHT_UNEATABLE_TEXT)

        yield WhatCanYouDoTopic()

        yield TextReply(
            "Хорошо. Давай поиграем.",
            ("Я очень люблю игру «Съедобное, несъедобное».", "Я очень люблю игру - «Съедобное, несъедобное»."),
            "Я играю лучше всех. А ты умеешь играть?"
        )

        rules = [
            "Правила этой игры очень простые:",
            "я загадаю слово, а ты отгадай, съедобное оно или несъедобное.",
            "Потом твоя очередь: загадай что-нибудь, а я отгадаю – съедобное оно или нет.",
        ]

        yield HelpReply(*rules, "Готов попробовать?")

        i_can:AgreeIntent = yield AgreeIntent()

        if i_can:
            yield TextReply("Тогда давай играть. Я начинаю.")
        else:
            yield TextReply(
                *rules,
                "Давай попробуем. Я начинаю."
            )

        while True:
            is_bot_riddle_eatable = self.choice((True, False))
            bot_riddle = self.get_eatable_riddle() if is_bot_riddle_eatable else self.get_uneatable_riddle()

            yield TextReply((
                f"Угадай, {bot_riddle} – это съедобное?",
                f"Угадай - - {bot_riddle} - - это съедобное?",
            ))

            yield HelpReply(
                f"Мы играем поочереди.",
                f"Сейчас я загадываю, а ты отгадываешь.",
                (f"Вот моя загадка: {bot_riddle} – это съедобное?", f"Вот моя загадка - - {bot_riddle} - - это съедобное?")
            )

            user_guess: EatableGuessIntent = yield EatableGuessIntent()

            if user_guess.is_eatable:
                if is_bot_riddle_eatable:
                    yield TextReply(next(user_right_eatable_text))
                    yield TextReply("Это съедобное.")
                else:
                    yield TextReply("Разве можно такое есть? Нет. Это несъедобное.")

            elif user_guess.is_uneatable:
                if is_bot_riddle_eatable:
                    yield TextReply("Не угадал. Это съедобное.")
                else:
                    yield TextReply(next(user_right_uneatable_text))
                    yield TextReply("Это несъедобное.")

            elif user_guess.dont_know:
                if is_bot_riddle_eatable:
                    yield TextReply("Сдаёшься? Разве это не звучит вкусно? Это съедобное.")
                else:
                    yield TextReply(f"Сдаёшься? Это несъедобное.")

            self._riddle_logger.log(
                riddle=bot_riddle,
                guess=user_guess.is_eatable,
                answer=is_bot_riddle_eatable,
                is_user=False
            )

            yield TextReply("Теперь твоя очередь. Скажи свою загадку.")
            yield HelpReply(
                "Сейчас твоя очередь загадывать.",
                "Придумай какой-нибудь предмет или еду.",
                "Попробуй обхитрить меня.",
                "Скажи свою загадку.",
            )

            user_riddle: EatableRiddleIntent = yield EatableRiddleIntent()
            bot_guess = self.is_eatable(user_riddle.riddle)

            if bot_guess:
                yield TextReply("Похоже это можно есть. Съедобное! Я угадала?")
            else:
                yield TextReply("Такое есть нельзя. Несъедобное! Правильно я говорю?")

            yield HelpReply(
                (f"Твоя загадка была: «{user_riddle.riddle}».", f"Твоя загадка была - - {user_riddle.riddle}."),
                "Я думаю, что это",
                "можно есть. Это съедобное!" if bot_guess else "нельзя есть. Несъедобное!",
                "Скажи, я отгадала твою загадку?"
            )

            bot_guessed_right: YouGuessedRightIntent = yield YouGuessedRightIntent()

            if bot_guessed_right.right:
                yield TextReply(self.choice((
                    "Это замечательно. Очень хорошо.",
                    "Я хорошо играю.",
                    "Ура! Это моя любимая игра.",
                    "Я справилась.",
                    "Я очень умная.",
                )))

            elif bot_guessed_right.wrong:
                yield TextReply(self.choice((
                    "Ну ничего. В следующий раз угадаю.",
                    "Ты молодец. Хитрая загадка.",
                    "Меня трудно обыграть, но у тебя получилось.",
                    "Это была хорошая загадка.",
                    "Не повезло мне.",
                )))
            else:
                yield TextReply(self.choice((
                    "Вот оно что! Ладно.",
                    "Хорошо играем. Давай ещё раз.",
                )))

            self._riddle_logger.log(
                riddle=user_riddle.riddle,
                guess=bot_guess,
                answer=bot_guess if bot_guessed_right.right else not bot_guess,
                is_user=True
            )

            yield TextReply(self.choice((
                "Моя очередь.",
                "Теперь я загадываю.",
            )))


class WhatCanYouDoTopic(Topic):
    def flow(self) -> Topic.Flow:
        while True:
            yield WhatCanYouDoIntent()

            yield TextReply(
                "Я умею играть в «Съедобное, несъедобное».",
                "Отгадай мои загадки и загадай свои.",
                "Если запутаешься, попроси меня помочь.",
                "А теперь давай играть.",
            )
