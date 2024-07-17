from typing import Optional
from pydantic import BaseModel


class LLMRequest(BaseModel):
    id: str
    prompt: str
    destination: Optional[str] = None
