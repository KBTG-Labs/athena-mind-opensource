from typing import Optional

from db.common import DBProvider, DBConfig, IDB
from db.dict import LocalDB
from db.redis import RedisDB


def create_db(db_provider: DBProvider, db_config: Optional[DBConfig]) -> IDB:
    match db_provider.lower():
        case DBProvider.LOCAL.value:
            return LocalDB()
        case DBProvider.REDIS.value:
            host = db_config.host
            return RedisDB(host=host)
        case _:
            raise ValueError(f"Unsupported DB provider: {db_provider}")
