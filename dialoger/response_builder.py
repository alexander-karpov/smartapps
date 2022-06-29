class ResponseBuilder:
    _text: list[str]
    _tts: list[str]
    _end_session: bool = False

    def __init__(self) -> None:
        self._text = []
        self._tts = []

    def append_text(self, text: str) -> None:
        if self._text \
            and not self._text[-1].endswith(' ') \
            and not text.startswith((',', '.', '!', '?')):
            self._text.append(' ')

        self._text.append(text)

    def append_tts(self, tts: str) -> None:
        if self._tts \
            and not self._tts[-1].endswith(' ') \
            and not tts.startswith((',', '.', '!', '?')):
            self._tts.append(' ')

        self._tts.append(tts)

    def end_session(self) -> None:
        self._end_session = True

    def build(self) -> dict:
        text = ''.join(self._text)[0:1024]
        tts = ''.join(self._tts)[0:1024]

        return {
            'response': { 'text': text, 'tts': tts, 'end_session': self._end_session },
            'version': '1.0'
        }
