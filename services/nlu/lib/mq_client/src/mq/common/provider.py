from abc import ABC, abstractmethod
from typing import Callable, List

from mq.common.dto import QueueDTO


class IMQConsumer(ABC):
    @abstractmethod
    def subscribe(self, topics: List[str]):
        raise NotImplementedError

    @abstractmethod
    def commit(self, asynchronous=True):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @abstractmethod
    def register_callback(callback: Callable[[QueueDTO], bool]):
        raise NotImplementedError

    @abstractmethod
    def consume(self):
        raise NotImplementedError


class IMQProducer(ABC):
    @abstractmethod
    def publish_message(self, topic: str, payload: QueueDTO):
        raise NotImplementedError
