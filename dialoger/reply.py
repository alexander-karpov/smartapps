from dialoger.response_builder import ResponseBuilder

class Reply:
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
