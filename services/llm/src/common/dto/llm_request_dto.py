from pydantic import BaseModel



class LLMRequestDTO(BaseModel):
    text: str
