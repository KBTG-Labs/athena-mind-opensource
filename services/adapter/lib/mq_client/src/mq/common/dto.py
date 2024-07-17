from typing import Any, Dict, Optional

from pydantic import BaseModel

from .exception import Error


class QueueDTO(BaseModel):
    id: str
    message: Dict[str, Any]
    source: Optional[str] = ''
    destination: Optional[str] = None
    error: Optional[Error] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'source': self.source,
            'message': self.message,
            'destination': self.destination,
            'error': self.error.model_dump() if self.error is not None else None,
        }
