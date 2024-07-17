import logging.config

from common.constant.domain import (
    APP_ADAPTER,
    DOMAIN_LLM,
    DOMAIN_VECTOR,
    INFRA_MQ_CLIENT,
)
from common.log.log import LogFilter, LogFormatter, LogLevel, LogTimezone


def get_logging_config(log_level: LogLevel, log_timezone: LogTimezone):
    return  {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "json_filter": {
                "()": LogFilter,
            }
        },
        "formatters": {
            "json_formatter": {
                "()": LogFormatter,
                "tz": log_timezone,
            },
        },
        "handlers": {
            "json_handler": {
                "filters": ["json_filter"],
                "formatter": "json_formatter",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["json_handler"], "level": log_level, "propagate": False},
            "opentelemetry": {"handlers": ["json_handler"], "level": log_level, "propagate": False},
            APP_ADAPTER: {"handlers": ["json_handler"], "level": log_level, "propagate": False},
            DOMAIN_LLM: {"handlers": ["json_handler"], "level": log_level, "propagate": False},
            DOMAIN_VECTOR: {"handlers": ["json_handler"], "level": log_level, "propagate": False},
            INFRA_MQ_CLIENT: {"handlers": ["json_handler"], "level": log_level, "propagate": False},
        },
    }

def configure_logging(log_level: LogLevel = "DEBUG", log_timezone: LogTimezone = 7):
    config = get_logging_config(log_level, log_timezone)
    logging.config.dictConfig(config)