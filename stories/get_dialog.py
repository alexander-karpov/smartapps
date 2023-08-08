from functools import lru_cache
from dialoger import Dialog


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=['алиса'])
    on, say = dialog.append_handler, dialog.append_reply

    @on('обновить', 'заново', 'снова', 'новая игра')
    async def _():
        say('Начинаем заново. Стреляй')

    @on()
    async def _():
        say('Будь как дома путник')

    return dialog
