from abc import ABC, abstractmethod
from typing import List

from internal.domain.entity import LLMRequest, LLMResponse


class ILLMService(ABC):
    @abstractmethod
    def process_messages(self, payloads: List[LLMRequest]) -> List[LLMResponse]:
        raise NotImplementedError
