from dialoger import Dialog
import random

def append_lets_play(dialog: Dialog) -> None:
    on, say, prompt = dialog.append_handler, dialog.append_reply, dialog.append_prompt

    @prompt()
    def _():
        say(random.choice((
            'А хочешь со мной поиграть?',
            'Давай лучше поиграем.',
            'Я хочу поиграть.',
        )))

        on('во что', 'во что будем играть', yes=True)(
            lets_play
        )

    @on(
        'давай играть',
        'хочешь поиграть',
        'давай поиграем ещё раз',
        'я хочу с тобой поиграть',
        'какие игры ты любишь играть',
        'давай поиграем в игру кальмары',
    )
    def lets_play():
        say(random.choice((
            'Я люблю играть в догонялки и в прятки.',
            'Х+аги В+аги хорошо прячется и догоняет человечков.',
            'Я могу находить прячущихся человечков и могу догонять.',
        )))

        say(random.choice((
            'Во что будем играть?',
            'Поиграем в догонялки или в прятки?',
        )))

        _append_games(dialog)

        @on('давай играть', 'начинаем игру')
        def _():
            say('В догонялки или в прятки?')

            _append_games(dialog)

        @on()
        def _():
            say('Х+аги В+аги играет только в догонялки и в прятки. Выбирай')

            _append_games(dialog)


def _append_games(dialog: Dialog):
    on, say = dialog.append_handler, dialog.append_reply

    # догонялки

    @on(
        'в догонялки',
        'догони меня',
        'я в догонялки хочу',
        'давай догоняй меня все равно не догонишь',
    )
    def _():
        say(random.choice((
            'Ты не сможешь убижать от Х+аги В+аги.',
            'Тебе от меня не убежать.'
        )))

        say(random.choice((
            'Я догоняю!',
            'Беги скорее, маленький человечик!',
            'Скорее беги, а то мне будет скучно.',
            'Я проголодался. Пора догнать человечка',
        )))

        @on()
        def _():
            say(random.choice((
                'Беги-беги. Я уже близко!',
                'Я у тебя за спиной.',
                'Я уже рядом. Наконец я покушаю!',
            )))

            @on()
            def _():
                say('Я догнал тебя. Ам!')

    # прятки

    @on('в прятки', 'я спрятался', 'попробуй найди меня', 'давай в прячешься человечки')
    def _():
        say(random.choice((
            'Х+аги В+аги чуит человечков.',
            'Ещё никто не спрятался от меня.',
            'Я так люблю искать человечков. Ням-ням.',
            'Это моя любимая игра когда хочется кушать.',
        )))

        say(random.choice((
            'Прячься скорее!',
            'Прячься, маленький человечик!',
            'Раз. Два. Пять. Х+аги В+аги идёт искать!',
            'Спрячься как следует.',
        )))

        @on()
        def _():
            say(random.choice((
                'Я чую тебя. Ты близко!',
                'Х+аги В+аги видит всё. Ты где-то рядом.',
                'Всё равно не спрячешься. Где ты?',
                'Я всё равно найду тебя. Ты где?',
            )))

            @on()
            def _():
                say('Я нашёл тебя. Ам!')
