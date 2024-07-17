from abc import ABC, abstractmethod

from common.dto import PublishedMessageDTO


class IProducerService(ABC):
    @abstractmethod
    def publish_message(self, payload: PublishedMessageDTO):
        raise NotImplementedError
