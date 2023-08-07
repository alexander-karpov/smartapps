import tensorflow_hub as hub
import numpy as np
import tensorflow_text

class BertEncoder:
    def __init__(self):
        self.embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")

    def __call__(self, texts: list[str]) -> np.ndarray:
        return self.embed(texts)

bert_encoder = BertEncoder()
