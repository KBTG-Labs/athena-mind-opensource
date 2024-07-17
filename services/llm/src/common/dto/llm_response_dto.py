from pydantic import BaseModel


class LLMResponseDTO(BaseModel):
    results: str | None
