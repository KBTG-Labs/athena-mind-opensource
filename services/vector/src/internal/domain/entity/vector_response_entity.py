from typing import List, Optional
from pydantic import BaseModel

from common.exception import Error


class VectorResponse(BaseModel):
    id: Optional[str] = ""
    results: Optional[List[List[float]]] = None
    destination: Optional[str] = None
    error: Optional[Error] = None
