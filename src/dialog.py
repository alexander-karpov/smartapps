from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, TypeVar, Union,  Generator, Optional
from generators import ShuffledSequence

TTopicChoice = TypeVar('TTopicChoice')


class ReplyBuilder:
    TextPart = Union[str, Tuple[str, str]]

    _display: List[str]
    _voice: List[str]
    _buttons: List[str]

    def __init__(self) -> None:
        self._display = []
        self._voice = []
        self._buttons = []


    def append_text(self, *text: TextPart):
        for t in text:
            if isinstance(t, tuple):
                self._display.append(t[0])
                self._voice.append(t[1])
            else:
                self._display.append(t)
                self._voice.append(t)


    def button(self, *title: str):
        self._buttons += title


class Reply(ABC):
    @abstractmethod
    def append_to(self, reply: 'ReplyBuilder') -> None:
        pass


class TextReply(Reply):
    _text: Tuple[ReplyBuilder.TextPart, ...]


    def __init__(self, *text: ReplyBuilder.TextPart) -> None:
        self._text = text


    def append_to(self, reply: ReplyBuilder) -> None:
        reply.append_text(*self._text)


class HelpReply(TextReply):
    pass


class Intent(ABC):
    @abstractmethod
    def match(self, command: str) -> bool:
        pass


class AnyIntent(Intent):
    def match(self, command: str) -> bool:
        return True


class Topic(ABC):
    Flow = Generator[Union[Reply, Intent, 'Topic'], Any, Any]

    _flow: Optional[Flow]
    _intent: Intent
    _help: List[HelpReply]
    _subtopics: List['Topic']
    _choice_seqs: Dict[Tuple[Any, ...], ShuffledSequence]

    def __init__(self) -> None:
        super().__init__()

        self._intent = AnyIntent()
        self._flow = None
        self._help = []
        self._subtopics = []
        self._choice_seqs = {}

    @abstractmethod
    def flow() -> Flow: pass

    def continue_(self, command: str, reply: ReplyBuilder) -> bool:
        for st in self._subtopics:
            is_matched = st.continue_(command, reply)

            if is_matched:
                self.append_help(reply)

                return True

        is_matched = self._intent.match(command)

        if not is_matched:
            return False

        self._help = []

        while True:
            try:
                if self._flow is None:
                    self._flow = self.flow()
                    action = next(self._flow)
                else:
                    action = self._flow.send(self._intent)
            except StopIteration:
                return True

            if isinstance(action, HelpReply):
                self._help.append(action)

            elif isinstance(action, Reply):
                action.append_to(reply)

            elif isinstance(action, Topic):
                action.continue_(command, reply)

                self._subtopics.append(action)

            elif isinstance(action, Intent):
                self._intent = action

                break

        return True

    def append_help(self, reply: ReplyBuilder) -> None:
        for h in self._help:
            h.append_to(reply)

    def choice(self, cases: Tuple[TTopicChoice, ...]) -> TTopicChoice:
        if cases in self._choice_seqs:
            return next(self._choice_seqs[cases])

        seq = ShuffledSequence(cases)
        self._choice_seqs[cases] = seq

        return next(seq)



class Dialog:
    _current_topic: Topic


    def __init__(self, start_topic: Topic):
        self._current_topic = start_topic


    def handle_command(self, command: str, reply: ReplyBuilder) -> None:
        handled = self._current_topic.continue_(command, reply)

        if not handled:
            self._current_topic.append_help(reply)
