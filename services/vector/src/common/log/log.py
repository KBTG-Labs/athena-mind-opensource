import json
import logging
import uuid
from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
from logging import Filter, Formatter, LogRecord, StreamHandler
from typing import Callable, Literal, Optional, TypeVar

R = TypeVar("R")

correlation_id = ContextVar("correlation_id", default=None)

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogTimezone = float

LOG_LEVEL: LogLevel = logging.DEBUG
LOG_TIMEZONE: LogTimezone = 0


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
            "@timestamp": record.asc_time,
            "request.id": record.correlation_id,
            "log.level": record.levelname,
            "log": {
                "origin": {
                    "file": {
                        "line": record.lineno,
                        "name": record.pathname
                    },
                },
            },
            "source": record.name,
            "message": record.message,
        }

        if record.levelno >= logging.ERROR and record.exc_info is not None:
            log_result["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_result, ensure_ascii=False)


class Logger:
    @staticmethod
    def change_log_level(log_level: LogLevel):
        global LOG_LEVEL
        LOG_LEVEL = log_level

    @staticmethod
    def change_log_timezone(log_timezone: LogTimezone):
        global LOG_TIMEZONE
        LOG_TIMEZONE = log_timezone

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
    def get_handler() -> StreamHandler:
        handler = StreamHandler()

        filter = LogFilter()
        handler.addFilter(filter)

        formatter = LogFormatter(tz=LOG_TIMEZONE)
        handler.setFormatter(formatter)

        return handler

    @staticmethod
    def get_logger(domain: str, level: Optional[LogLevel] = None) -> logging.Logger:
        log_level = level or LOG_LEVEL
        logger = logging.getLogger(domain)

        logger.setLevel(log_level)
        logger.handlers = [Logger.get_handler()]
        logger.propagate = False

        return logger
