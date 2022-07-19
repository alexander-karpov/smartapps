from abc import ABC, abstractmethod
from typing import Iterable
from dialoger.response_builder import ResponseBuilder


class Reply(ABC):
    @abstractmethod
    def append_to(self, response_builder: ResponseBuilder) -> None: ...


class TextReply(Reply):
    _text: list[str]
    _tts: list[str]
    _end: bool

    def __init__(self, *parts: str | tuple[str,str], end:bool = False) -> None:
        self._text = []
        self._tts = []
        self._end = end

        for  part in parts:
            match part:
                case str(text), str(tts):
                    self._text.append(text)
                    self._tts.append(tts)
                case str(part):
                    self._text.append(part)
                    self._tts.append(part.replace('+', ''))
                case _:
                    raise ValueError(f'Invalid type for parts item: {part}')

    def append_to(self, response_builder: ResponseBuilder) -> None:
        for t in self._text:
            response_builder.append_text(t)

        for t in self._tts:
            response_builder.append_tts(t)

        if self._end:
            response_builder.end_session()


class ImagesReply(Reply):
    _images: Iterable[str]

    def __init__(self, images: Iterable[str]) -> None:
        self._images = images

    def append_to(self, response_builder: ResponseBuilder) -> None:
        for i in self._images:
            response_builder.append_image(i)


class CardReply(Reply):
    _image: str

    def __init__(self, image: str) -> None:
        self._image = image

    def append_to(self, response_builder: ResponseBuilder) -> None:
        if self._image:
            response_builder.set_card_image(self._image)
