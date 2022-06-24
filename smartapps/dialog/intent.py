from sys import flags
import numpy as np
from smartapps.dialog.bert_encoder import bert_encoder
from smartapps.dialog.response_builder import ResponseBuilder


class Intent:
    samples: tuple[str, ...]
    threshold: float

    def __init__(self, *samples: str, threshold = 0.9) -> None:
        self.samples = samples
        self.threshold = threshold
        self.encoder = bert_encoder

    def match(self, text) -> bool:
        vectors = self.encoder.transform([text, *self.samples])
        score = max(vectors[1:].dot(vectors[0]))

        return score >= self.threshold
