from enum import Enum
from pydantic import BaseModel, model_serializer


class ErrorCode(str, Enum):
    MAXIMUM_RETRIES_REACH = 'MAXIMUM_RETRIES_REACH'


class Error(BaseModel):
    code: ErrorCode
    detail: str

    @model_serializer
    def serialize_model(self):
        return {
            "code": str(self.code.value),
            "detail": self.detail,
        }
