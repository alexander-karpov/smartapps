import torch
import logging
import numpy as np
from transformers import AutoTokenizer, AutoModel # type: ignore
from dialoger.set_global_logging_level import set_global_logging_level


set_global_logging_level(logging.ERROR, ['transformers'])


class BertEncoder:
    def __init__(self, model_name):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def __call__(self, texts: list[str]) -> np.ndarray:
        t = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

        with torch.no_grad():
            model_output = self.model(**{k: v.to(self.model.device) for k, v in t.items()})

        embeddings = model_output.last_hidden_state[:, 0, :]
        embeddings = torch.nn.functional.normalize(embeddings)  # type: ignore
        return embeddings.cpu().numpy()


bert_encoder = BertEncoder("cointegrated/LaBSE-en-ru")
