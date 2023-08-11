from typing import Any
import tensorflow_hub as hub
import numpy as np
import tensorflow_text


class Encoder:
    embed: Any

    def __init__(self) -> None:
        self.embed = None

    def __call__(self, texts: list[str]) -> np.ndarray:
        if not self.embed:
            self.embed = hub.load(
                "https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3"
            )

        return self.embed(texts)


encoder = Encoder()
