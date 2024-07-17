from pydantic import BaseModel
from typing import List


class VectorResponseDTO(BaseModel):
    results: List[List[float]] | None
