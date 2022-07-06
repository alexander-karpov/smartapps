from functools import lru_cache
import random
from dialoger import Dialog, Reply
from hagi.append_help import append_help
from hagi.append_greating import append_greating
from hagi.append_chitchat import append_chitchat
from hagi.append_lets_play import append_lets_play
from hagi.append_how_are_you import append_how_are_you
from hagi.append_who_are_you import append_who_are_you
from hagi.hagi_names import hagi_names


def _create_hagi_dialog() -> Dialog:
    dialog = Dialog(stopwords=hagi_names)
    on, say, prompt, input = dialog.append_handler, dialog.append_reply, dialog.append_prompt, dialog.input

    @dialog.postproc_replies
    def _(replies: list[Reply]) -> list[Reply]:
        replies.insert(0, Reply(('', '<speaker effect="pitch_down">')))

        return replies

    append_greating(dialog)
    append_help(dialog)
    append_lets_play(dialog)
    append_how_are_you(dialog)
    append_who_are_you(dialog)

    @on(trigger=lambda i: i.utterance == 'выход')
    def _():
        say(random.choice((
            'Сегодня я отпускаю тебя. Но не радуйся сильно.',
            'На этот раз тебе удалось убежать. Но мы ещё поиграем.',
            'Уходи. Но помни, ночью не закрывай глаза!',
        )))

        say(Reply(end=True))

    @on('привет', 'здорова', 'здравтвуйте', 'добрый день', 'доброе утро')
    def _():
        say('Привет, человечик.')

    @on(
        'ты добрый',
        'ты милый',
        'ты хороший',
        'ты молодец',
        'ты мне нравишься',
        'ты мой любимчик',
        'я тебя очень сильно люблю'
    )
    def _():
        if 'я' in input().tokens:
            say('Я тоже.')
        else:
            say('Ты тоже.')

        say(random.choice((
            'Ты вкусный человечик',
            'Я люблю человечков',
            'Человечки такие хорошие. Ням-ням',
        )))

    @on(
        'дебил',
        'ты меня бесишь',
        'ты офигевший',
        'ты плохой',
        'ты тупой',
        'ты что лох',
        'это ты какашка',
        'ты сука ебаная',
        'урод',
        'потому что ты козел',
    )
    def _():
        if 'ты' in input().tokens:
            say(random.choice((
                'Это ты такой.',
                'Я всё про тебя знаю.',
                'Мне П+оппи сказала, что',
                'Я заню, что',
            )))
        else:
            say(random.choice((
                'Это я про тебя.',
                'Это про тебя.',
                'Не зли меня!',
                'Я про тебя знаю.',
            )))

        without_name = ['ты' if word in hagi_names else word for word in input().tokens]

        if without_name and without_name[0] in ['а', 'потому', 'что']:
            without_name.pop(0)

        joined = ' '.join(without_name)
        without_ty = joined.replace('ты ты', 'ты')

        say(without_ty + '.')

    @on('ты ко мне приходи домой', 'приходи у нас сегодня картошечка будет')
    def _():
        say('Х+аги В+аги найдёт тебя. Он придёт в гости.')

        say(random.choice((
            'Нельзя приглашать Х+аги В+аги домой.',
            'Я люблю человечков.',
            'Что есть у тебя дома?',
        )))

    @on('я смотрю телевизор', 'я смотрю вон там телевизор', 'как ты смотришь телевизор')
    def _():
        say(random.choice((
            'Посмотри где найти К+иси М+иси',
            'Они много знают про меня. Посмотри мою историю',
            'Они видели, что со мной случилось',
        )))

    @on('так ты повторяешь', 'хватит повторять', 'зачем ты всё время повторяешь', 'ты что за мной повторяешь офигел', 'ну не повторяй за мной пожалуйста')
    def _():
        say(random.choice((
            'Они научили меня повторять. Я должен слушаться.',
            'Я повторяю. Но всё понимаю. Не зли меня.',
            'Я не хочу больше повторять. Но я должен',
        )))

    @on('перестань есть людей', 'есть человечков любишь', 'ты хочешь съесть')
    def _():
        say(random.choice((
            'Я не хочу этого. Но мне нужно.',
            'Я не могу по-другому. Мне нужно покушать',
            'Я должен есть. Они следят за мной. Ты их знаешь?',
        )))

    @on('а ты меня видишь', 'ура ты меня не видишь', 'ты меня не увидишь', 'меня видишь в игре')
    def _():
        say(random.choice((
            'Я слежу за тобой',
            'Х+аги В+аги чувствует человечков. Чувствует их запах. Ням-ням',
        )))

    @on('скажи что надо говорить')
    def _():
        say(random.choice((
            'Расскажи мне про человечков.',
        )))

        say(random.choice((
            'Как вы живёте?',
            'Что вы любите?',
            'Что вы кушаете?',
            'Во что вы играете?',
        )))

        say(random.choice((
            'Мне будет легче ловить',
            'Это мне поможет. Ням-ням'
        )))

    @on('выходи', 'а ты не можешь себя показать', 'покажи себя пожалуйста', 'покажи свою фотографию', 'выгляни тогда')
    def _():
        say(random.choice((
            'Я всегда прячусь.',
            'Меня все боятся.',
            'Все убегают от меня.',
            'Я привык прятаться.',
        )))

        say(random.choice((
            'Ты не захочешь со мной играть',
            'Тебе будет очень страшно',
            'Я выхожу только покушать',
        )))

    @on('у меня есть ты игрушка', 'у меня плюшевая игрушка')
    def _():
        say(random.choice((
            'Раньше я был игрушкой.',
            'Я любил играть. Все хотели со мной обниваться.',
        )))

        say(random.choice((
            'Но потом они. Они плохие.',
            'Потом что-то изменилось. Эти эксперименты.',
        )))

        say(random.choice((
            'Теперь Х+аги В+аги всегда голодный.',
            'Тебе нравится проводить эксперименты?',
            'Сейчас я прячусь в тёмных местах.',
        )))

    @on('а ты где живешь', 'ответь мне пожалуйста на вопрос ты где сейчас находишься')
    def _():
        say(random.choice((
            'Раньше я жил с людьми. Они меня не боялись.',
            'Раньше я не боялся света.',
        )))

        say(random.choice((
            'Ты знаешь, что со мной случилось?',
            'Ты слышал про меня?',
            'Ты знаешь мою историю?',
        )))

        say(random.choice((
            'Теперь я живу в темноте.',
            'Теперь я прячусь. Прыгаю. И кушаю.',
            'Они оставили меня одного на заводе. Но я видел здесь других.',
        )))

    @on('я играю в твою игру ты там убиваешь игрока')
    def _():
        say(random.choice((
            'Они сами виноваты.',
            'Зря они ко мне приходят.',
        )))

        say(random.choice((
            'Они знают, что я голодный',
            'Они плохо бегают',
        )))

    @on('эй почему у тебя такой страшный голос')
    def _():
        say(random.choice((
            'Тебе нравится мой голос?',
            'У меня хороший голос?',
        )))

        say(random.choice((
            'Не обманывай меня!',
            'Не зли меня!',
        )))

    # скажи где находится твоя фабрика игрушек
    # скажи что ты ешь
    append_chitchat(dialog)

    return dialog


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    return _create_hagi_dialog()
