from abc import ABC, abstractmethod
from typing import List

from internal.domain.entity import LLMRequest, LLMResponse


class ILLMModel(ABC):
    @abstractmethod
    def generate_response(self, message: LLMRequest) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    def generate_batch_responses(self, messages: List[LLMRequest]) -> List[LLMResponse]:
        raise NotImplementedError
