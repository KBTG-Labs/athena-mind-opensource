from abc import ABC, abstractmethod
from typing import List

class IVectorModel(ABC):
    @abstractmethod
    def process(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError