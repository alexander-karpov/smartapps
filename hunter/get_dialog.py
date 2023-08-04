from functools import lru_cache
from dialoger import Dialog, CardReply


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=['алиса'])
    on, say, prompt, input = dialog.append_handler, dialog.append_reply, dialog.append_prompt, dialog.input

    @on('обновить', 'заново', 'снова', 'новая игра')
    async def _():
        say('Начинаем заново. Стреляй')

    @on()
    async def _():
        say('Будь как дома путник')

    return dialog
