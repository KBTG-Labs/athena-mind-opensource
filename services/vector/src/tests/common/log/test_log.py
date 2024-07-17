import pytest
import logging
import json

from logging import LogRecord
from unittest.mock import MagicMock, patch

from common.log.log import LogFilter, LogFormatter, Logger, correlation_id


@pytest.fixture(autouse=True)
def clear_system_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("LOG_TIMEZONE", raising=False)


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
def test_get_logger_with_default(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    logger_name = 'test_logger'
    logger = Logger.get_logger(logger_name)

    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
    assert logger.level == logging.DEBUG


@pytest.mark.logger
def test_get_logger():
    logger_name = 'test_logger'
    logger = Logger.get_logger(logger_name, "ERROR")

    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
    assert logger.level == logging.ERROR


@patch('common.log.log.StreamHandler')
@patch('common.log.log.LogFilter')
@patch('common.log.log.LogFormatter')
@pytest.mark.logger
def test_get_logging_handler(mock_LogFormatter, mock_LogFilter, mock_StreamHandler):
    Logger.get_handler()

    mock_StreamHandler.assert_called_once()
    handler = mock_StreamHandler.return_value

    mock_LogFilter.assert_called_once()
    handler.addFilter.assert_called_once_with(mock_LogFilter.return_value)

    mock_LogFormatter.assert_called_once()
    handler.setFormatter.assert_called_once_with(
        mock_LogFormatter.return_value)


@pytest.mark.logger
def test_get_logger_sets_correct_with_assigned_log_level():
    domain = "test_domain"
    custom_level = logging.CRITICAL

    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        Logger.get_logger(domain, custom_level)

        mock_logger.setLevel.assert_called_once_with(custom_level)


@pytest.mark.logger
def test_get_logger_sets_correct_with_default_global_log_level():
    domain = "test_domain"
    global_level = logging.DEBUG

    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        Logger.get_logger(domain)

        mock_logger.setLevel.assert_called_once_with(global_level)


@pytest.mark.logger
def test_get_logger_sets_correct_with_updated_global_log_level():
    domain = "test_domain"
    global_level = logging.ERROR

    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        Logger.change_log_level(global_level)
        Logger.get_logger(domain)

        mock_logger.setLevel.assert_called_once_with(global_level)


@pytest.mark.logger
def test_get_logger_sets_correct_with_overwritten_log_level():
    domain = "test_domain"
    global_level = logging.ERROR
    overwritten_level = logging.CRITICAL

    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        Logger.change_log_level(global_level)
        Logger.get_logger(domain, overwritten_level)

        mock_logger.setLevel.assert_called_once_with(overwritten_level)


@patch('common.log.log.StreamHandler')
@patch('common.log.log.LogFilter')
@patch('common.log.log.LogFormatter')
@pytest.mark.logger
def test_get_logger_sets_correct_with_default_global_log_timezone(
    mock_LogFormatter,
    mock_LogFilter,
    mock_StreamHandler,
):
    default_level = 0

    Logger.get_handler()

    mock_LogFormatter.assert_called_once_with(tz=default_level)


@patch('common.log.log.StreamHandler')
@patch('common.log.log.LogFilter')
@patch('common.log.log.LogFormatter')
@pytest.mark.logger
def test_get_logger_sets_correct_with_updated_global_log_timezone(
    mock_LogFormatter,
    mock_LogFilter,
    mock_StreamHandler,
):
    global_level = 0

    Logger.change_log_timezone(global_level)
    Logger.get_handler()

    mock_LogFormatter.assert_called_once_with(tz=global_level)
