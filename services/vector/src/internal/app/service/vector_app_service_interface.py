from abc import ABC, abstractmethod
from typing import List

from common.dto import ConsumedMessageDTO


class IVectorApplicationService(ABC):
    @abstractmethod
    def handle_queue(self, payloads: List[ConsumedMessageDTO]):
        raise NotImplementedError
