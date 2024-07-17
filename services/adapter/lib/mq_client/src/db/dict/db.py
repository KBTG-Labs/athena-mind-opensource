from typing import Dict, Any

from db.common import IDB


class LocalDB(IDB):
    def __init__(self):
        self.repo: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self.repo.get(key)

    def set(self, key: str, item: Any):
        self.repo[key] = item

    def delete(self, key: str):
        if key in self.repo:
            del self.repo[key]
