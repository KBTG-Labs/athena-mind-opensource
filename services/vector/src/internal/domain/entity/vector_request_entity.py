from typing import List, Optional
from pydantic import BaseModel


class VectorRequest(BaseModel):
    id: str
    texts: List[str]
    destination: Optional[str] = None

    def to_request(self) -> List[str]:
        return self.texts
