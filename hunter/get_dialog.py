from functools import lru_cache
from dialoger import Dialog, CardReply
from renderer import Renderer, ImagesUploader, update, shoot


renderer = Renderer()
uploader = ImagesUploader()


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    dialog = Dialog(stopwords=['алиса'])
    on, say, prompt, input = dialog.append_handler, dialog.append_reply, dialog.append_prompt, dialog.input

    @on('обновить', 'заново', 'снова', 'новая игра')
    async def _():
        say('Начинаем заново. Стреляй')
        update()

        image_id, *_= await uploader.upload([renderer.render()])
        say(CardReply(image_id))

    @on(trigger=lambda i: i.number is not None)
    async def _():
        int_shot = int(input().number or 0)

        say(f'Выстрел на {int_shot}')
        shoot(int_shot)

        image_id, *_= await uploader.upload([renderer.render()])
        say(CardReply(image_id))

    @on()
    async def _():
        say('Будь как дома путник')

        image_id, *_= await uploader.upload([renderer.render()])
        say(CardReply(image_id))

    return dialog
