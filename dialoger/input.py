class Input:
    _request: dict

    def __init__(self, request:dict):
        self._request = request

    @property
    def is_new_session(self) -> bool:
        return self._request["session"]["new"]

    @property
    def tokens(self) -> list[str]:
        return self._request["request"]["nlu"]["tokens"]

    @property
    def utterance(self) -> str:
       return self._request["request"]["original_utterance"]

    @property
    def is_ping(self) -> bool:
        return  "ping" in self.utterance