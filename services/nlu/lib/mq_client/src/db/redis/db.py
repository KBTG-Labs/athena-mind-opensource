import asyncio

from typing import Dict, Any

from db.common import IDB


class RedisDB(IDB):
    def __init__(self, host: str):
        self.repo: Dict[str, asyncio.Future] = {}  # Redis Client

    def get(self, key: str) -> asyncio.Future | None:
        pass

    def set(self, key: str, item: Any):
        pass

    def delete(self, key: str):
        pass
