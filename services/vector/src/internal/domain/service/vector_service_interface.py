from abc import ABC, abstractmethod
from typing import Iterator, List

from internal.domain.entity import VectorRequest, VectorResponse


class IVectorService(ABC):
    @abstractmethod
    def process_message(self, payload: VectorRequest) -> VectorResponse:
        raise NotImplementedError
    
    @abstractmethod
    def process_messages(self, payloads: List[VectorRequest]) -> Iterator[VectorResponse]:
        raise NotImplementedError
