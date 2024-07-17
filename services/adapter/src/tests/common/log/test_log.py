import json
import logging
from logging import LogRecord
from unittest.mock import MagicMock

import pytest

from common.log.config import configure_logging
from common.log.log import LogFilter, LogFormatter, Logger, correlation_id


@pytest.mark.logger
def test_log_filter():
    log_filter = LogFilter()
    record = MagicMock()

    # Test when correlation_id is set
    correlation_id.set('test-correlation-id')
    result = log_filter.filter(record)
    assert result is True
    assert record.correlation_id == 'test-correlation-id'

    # Test when correlation_id is not set
    correlation_id.set(None)
    result = log_filter.filter(record)
    assert result is True
    assert record.correlation_id is None


@pytest.mark.logger
def test_log_formatter():
    TIMEZONE = 9
    log_formatter = LogFormatter(tz=TIMEZONE)

    record = LogRecord(
        name='test_logger',
        level=logging.INFO,
        pathname='test_path',
        lineno=10,
        msg='Test message',
        args=(),
        exc_info=None
    )
    record.correlation_id = 'test-correlation-id'
    record.getMessage = lambda: 'Test message'

    formatted_log = log_formatter.format(record)
    log_dict = json.loads(formatted_log)

    assert log_dict['message'] == 'Test message'
    assert log_dict['log.level'] == 'INFO'
    assert log_dict['log']['origin']['file']['line'] == 10
    assert log_dict['log']['origin']['file']['name'] == 'test_path'
    assert log_dict['source'] == 'test_logger'
    assert log_dict['request.id'] == 'test-correlation-id'
    assert log_dict['@timestamp'] is not None
    assert "+09:00" in log_dict['@timestamp']



@pytest.mark.logger
def test_register_correlation_id_mq():
    @Logger.register_correlation_id_mq
    def sample_function():
        correlation_id.set('test-correlation-id')
        return correlation_id.get()

    result = sample_function()
    assert result == "test-correlation-id"
    assert isinstance(result, str)

    # Ensure correlation_id is reset
    assert correlation_id.get() is None


@pytest.mark.logger
def test_get_logger():
    configure_logging(log_level="DEBUG")
    logger_name = "service.llm.client"
    logger = Logger.get_logger(logger_name)

    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
    assert logger.level == logging.DEBUG
