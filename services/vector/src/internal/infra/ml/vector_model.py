from typing import List

from sentence_transformers import SentenceTransformer
from transformers.utils.logging import add_handler, disable_default_handler

from common.constant.domain import INFRA_VECTOR as DOMAIN
from common.decorator import trace
from common.log import Logger
from internal.domain.ml import IVectorModel


class VectorModel(IVectorModel):
    def __init__(
        self,
        model_path: str,
        model_batch_size: int,
        model_max_characters: int,
    ):
        self.logger = Logger.get_logger(DOMAIN)

        # Config Transformers Logger
        disable_default_handler()
        add_handler(Logger.get_handler())

        self.model = SentenceTransformer(model_path)
        self.model_batch_size = model_batch_size
        self.model_max_characters = model_max_characters

    @trace
    def _process(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        for i in range(0, len(texts), self.model_batch_size):
            vector = self.model.encode(
                [text[:self.model_max_characters] for text in texts[i:i+self.model_batch_size]])
            vectors.extend(vector)
        return vectors

    @trace
    def process(self, texts: List[str]) -> List[List[float]]:
        self.logger.info(f"process (payload:{texts})")
        return self._process(texts)
