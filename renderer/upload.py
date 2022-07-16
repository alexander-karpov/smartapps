import os
import io
import asyncio
from PIL.Image import Image
import httpx

class ImageUploader:
    _cache: dict[str, str]

    def __init__(self) -> None:
        self._cache = {}

    async def upload(self, images: list[Image]):
        dialoder_renderer_skill_id = "75c022e8-3076-4b92-90c8-44ab38d29950"
        base_url = f"https://dialogs.yandex.net/api/v1/skills/{dialoder_renderer_skill_id}/images"
        headers = {"Authorization": f"OAuth {os.environ['DIALOGS_OAUTH']}"}

        async with httpx.AsyncClient(headers=headers, base_url=base_url) as client:
            responses = await asyncio.gather(
                *(client.post('', files={'file': self._image_to_file(i)}) for i in images)
            )

            return [r.json() for r in responses]

    def _image_to_file(self, image: Image) -> bytes:
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            return output.getvalue()
