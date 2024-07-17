from abc import ABC, abstractmethod
from typing import Any


class IDB(ABC):
    @abstractmethod
    def get(key: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def set(key: str, item: Any):
        raise NotImplementedError

    @abstractmethod
    def delete(key: str):
        raise NotImplementedError
