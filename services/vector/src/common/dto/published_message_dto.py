from typing import TypeVar, Optional, Generic
from pydantic import BaseModel, model_serializer

from common.exception import Error

T = TypeVar('T')


class PublishedMessageDTO(BaseModel, Generic[T]):
    id: str
    message: T
    source: Optional[str] = ''
    destination: Optional[str] = None
    error: Optional[Error] = None

    @model_serializer
    def serialize_model(self):
        return {
            'id': self.id,
            'source': self.source,
            'message': self.message,
            'destination': self.destination,
            'error': self.error.model_dump() if self.error is not None else None,
        }
