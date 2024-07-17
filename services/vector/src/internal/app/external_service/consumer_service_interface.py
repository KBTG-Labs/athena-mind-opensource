from abc import ABC, abstractmethod
from typing import List, Any


class IConsumerService(ABC):
    @abstractmethod
    def process(self, messages: List[Any]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def consume(self) -> List[Any] | None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, topics: List[str]):
        raise NotImplementedError

    @abstractmethod
    def commit(self, asynchronous=True):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError
