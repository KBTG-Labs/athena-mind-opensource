from typing import Optional
from enum import Enum
from pydantic import BaseModel


class DBConfig(BaseModel):
    host: Optional[str] = ""


class DBProvider(Enum):
    LOCAL = "local"
    REDIS = "redis"
