from typing import Optional
from pydantic import BaseModel

from common.exception import Error


class LLMResponse(BaseModel):
    id: Optional[str] = ""
    results: Optional[str] = None
    destination: Optional[str] = None
    error: Optional[Error] = None
