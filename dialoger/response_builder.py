from typing import Any


DialogResponse = dict[Any, Any]


class ResponseBuilder:
    _text: list[str]
    _tts: list[str]
    _images: list[str]
    _card_image: str | None
    _end_session: bool = False

    def __init__(self) -> None:
        self._text = []
        self._tts = []
        self._images = []
        self._card_image = None

    def append_text(self, text: str) -> None:
        if not text:
            return

        if (
            self._text
            and not self._text[-1].endswith(" ")
            and not text.startswith((",", ".", "!", "?"))
        ):
            self._text.append(" ")

        self._text.append(text)

    def append_tts(self, tts: str) -> None:
        if not tts:
            return

        if (
            self._tts
            and not self._tts[-1].endswith(" ")
            and not tts.startswith((",", ".", "!", "?"))
        ):
            self._tts.append(" ")

        self._tts.append(tts)

    def append_image(self, image_id: str) -> None:
        self._images.append(image_id)

    def set_card_image(self, image_id: str) -> None:
        assert self._card_image is None, "Картинка ещё не задана"

        self._card_image = image_id

    def end_session(self) -> None:
        self._end_session = True

    def build(self) -> DialogResponse:
        text = "".join(self._text)[0:1024]
        tts = "".join(self._tts)[0:1024]
        card = None

        if self._images:
            card = {
                "type": "ImageGallery",
                "items": [{"image_id": id} for id in self._images],
            }

        if self._card_image:
            card = {
                "type": "BigImage",
                "image_id": self._card_image,
            }

        return {
            "response": {
                "text": text,
                "tts": tts,
                "end_session": self._end_session,
                "card": card,
            },
            "version": "1.0",
        }
