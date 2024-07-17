from typing import List
from enum import Enum
from pydantic import BaseModel


class MQConfig(BaseModel):
    host: str
    consume_topics: List[str]
    consume_timeout: float


class MQProvider(Enum):
    KAFKA = "kafka"
