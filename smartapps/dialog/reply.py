from smartapps.dialog.response_builder import ResponseBuilder

class Reply:
    _text: list[str]
    _tts: list[str]

    def __init__(self, *parts: str | tuple[str,str]) -> None:
        self._text = []
        self._tts = []

        for  part in parts:
            match part:
                case str(text), str(tts):
                    self._text.append(text)
                    self._tts.append(tts)
                case str(part):
                    self._text.append(part)
                    self._tts.append(part)
                case _:
                    raise ValueError(f'Invalid type for parts item: {part}')

    def append_to(self, response_builder: ResponseBuilder) -> None:
        for t in self._text:
            response_builder.append_text(t)

        for t in self._tts:
            response_builder.append_tts(t)
