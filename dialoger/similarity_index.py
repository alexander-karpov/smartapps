import faiss
import numpy as np
from dialoger.bert_encoder import BertEncoder, bert_encoder


class SimilarityIndex:
    encoder: BertEncoder
    index: faiss.IndexFlatIP

    def __init__(self, encoder: BertEncoder, dim):
        self.encoder = encoder
        self.index = faiss.IndexFlatIP(dim)
        self.phrase_to_id = {}

    def add(self, phrases: tuple[str, ...]) -> tuple[int, ...]:
        new_phrases = [t for t in phrases if t not in self.phrase_to_id]

        if new_phrases:
            vectors = self.encoder(new_phrases)

            assert vectors.shape[1] == self.index.d
            assert self.index.is_trained

            start_id = self.index.ntotal
            self.index.add(vectors)

            for i, text in enumerate(new_phrases):
                self.phrase_to_id[text] = start_id + i

        return tuple(self.phrase_to_id[t] for t in phrases)

    def search(self, text: str, range) -> np.ndarray:
        _, D, I = self.index.range_search(self.encoder([text]), range)

        return I[np.argsort(1 - D)]

    def most_similar(self, intents: list[tuple[str, ...]], text: str, range = 0.87) -> int | None:
        intent_to_ids = [self.add(phrases) for phrases in intents]
        nearest = list(self.search(text, range))

        if not nearest:
            return None

        # Сортируем интенты по позициям их фраз в массиве nearest
        intent_to_nearest = [(i, sorted([nearest.index(id) if id in nearest else np.inf for id in ids])) for i, ids in enumerate(intent_to_ids)]
        intent_to_nearest_sorted = sorted(intent_to_nearest, key=lambda item: item[1])

        for i, ids_indices in intent_to_nearest_sorted:
            if ids_indices and ids_indices[0] is not np.inf:
                return i

        return None

similarity_index = SimilarityIndex(bert_encoder, 312)
