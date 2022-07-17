from functools import lru_cache
from dialoger import Dialog, ImagesReply
from renderer import Renderer, ImagesUploader


renderer = Renderer()
uploader = ImagesUploader()


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=['алиса'])
    on, say, prompt, input = dialog.append_handler, dialog.append_reply, dialog.append_prompt, dialog.input

    @on()
    async def _():
        say('Будь как дома путник я ни в чём не откажу')

        ids = await uploader.upload(renderer.render())

        say(ImagesReply(ids))

    return dialog
