from pydantic import BaseModel
from typing import List

class VectorRequestDTO(BaseModel):
    texts: List[str]
