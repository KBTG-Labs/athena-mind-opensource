import json
import logging
import logging.config
import uuid
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from logging import Filter, Formatter, LogRecord
from typing import Callable, Literal, Optional, TypeVar

from starlette.types import Receive, Scope, Send

R = TypeVar('R')
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogTimezone = float

correlation_id = ContextVar('correlation_id', default=None)


@dataclass
class CorrelationIdMiddleware:
    app: 'CorrelationIdMiddleware'

    correlation_id: ContextVar[Optional[str]] = correlation_id

    async def __call__(self, scope: 'Scope', receive: 'Receive', send: 'Send') -> None:
        new_id = str(uuid.uuid4())
        self.correlation_id.set(new_id)

        await self.app(scope, receive, send)
        return


class LogFilter(Filter):
    def filter(self, record):
        record.correlation_id = correlation_id.get()
        return True


class LogFormatter(Formatter):

    def __init__(self, tz: float, **kwargs):
        super().__init__(**kwargs)
        self.timezone = timezone(timedelta(hours=tz))

    def format(self, record: LogRecord):
        record.message = record.getMessage()
        record.asc_time = datetime.now(self.timezone).isoformat()
        log_result = {
            '@timestamp': record.asc_time,
            'request.id': record.correlation_id,
            'log.level': record.levelname,
            'log': {
                "origin": {
                    "file": {
                        "line": record.lineno,
                        "name": record.pathname
                    },
                },
            },
            'source': record.name,
            'message': record.message,
        }

        if record.levelno >= logging.ERROR and record.exc_info is not None:
            log_result['exc_info'] = self.formatException(record.exc_info)

        return json.dumps(log_result, ensure_ascii=False)

class Logger:

    @staticmethod
    def register_correlation_id_mq(func: Callable[..., R]) -> Callable[..., R]:
        def wrapper(*args, **kwargs) -> R:
            # Register Correlation ID
            new_id = str(uuid.uuid4())
            correlation_id.set(new_id)
            try:
                results = func(*args, **kwargs)
                return results
            finally:
                # Remove Correlation ID
                correlation_id.set(None)
        return wrapper

    @staticmethod
    def get_logger(domain: str) -> logging.Logger:
        logger = logging.getLogger(domain)
        return logger