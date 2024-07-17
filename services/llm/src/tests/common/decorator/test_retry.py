import pytest

from unittest.mock import MagicMock
from common.exception import ErrorCode

from common.decorator import retry


@pytest.fixture
def logger():
    return MagicMock()


@pytest.mark.asyncio
@pytest.mark.retry_decorator
async def test_async_retry_success(logger):
    @retry(max_retries=3, delay=0.01, logger=logger)
    async def success_fn():
        return "success"

    response = await success_fn()

    assert response.results == "success"
    assert response.error is None
    logger.warning.assert_not_called()
    logger.error.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.retry_decorator
async def test_async_retry_failure_then_success(logger):
    counter = 0

    @retry(max_retries=3, delay=0.01, logger=logger)
    async def flaky_fn():
        nonlocal counter
        counter += 1
        if counter < 3:
            raise ValueError("Temporary failure")
        return "success"

    response = await flaky_fn()

    assert response.results == "success"
    assert response.error is None
    assert logger.warning.call_count == 2
    logger.error.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.retry_decorator
async def test_async_retry_failure(logger):
    @retry(max_retries=3, delay=0.01, logger=logger)
    async def failure_fn():
        raise ValueError("Permanent failure")

    response = await failure_fn()

    assert response.results is None
    assert response.error is not None
    assert response.error.code == ErrorCode.MAXIMUM_RETRIES_REACH
    assert response.error.detail == "Permanent failure"
    assert logger.warning.call_count == 2
    assert logger.error.call_count == 1


@pytest.mark.retry_decorator
def test_sync_retry_success(logger):
    @retry(max_retries=3, delay=0.01, logger=logger)
    def success_fn():
        return "success"

    response = success_fn()

    assert response.results == "success"
    assert response.error is None
    logger.warning.assert_not_called()
    logger.error.assert_not_called()


@pytest.mark.retry_decorator
def test_sync_retry_failure_then_success(logger):
    counter = 0

    @retry(max_retries=3, delay=0.01, logger=logger)
    def flaky_fn():
        nonlocal counter
        counter += 1
        if counter < 3:
            raise ValueError("Temporary failure")
        return "success"

    response = flaky_fn()

    assert response.results == "success"
    assert response.error is None
    assert logger.warning.call_count == 2
    logger.error.assert_not_called()


@pytest.mark.retry_decorator
def test_sync_retry_failure(logger):
    @retry(max_retries=3, delay=0.01, logger=logger)
    def failure_fn():
        raise ValueError("Permanent failure")

    response = failure_fn()

    assert response.results is None
    assert response.error is not None
    assert response.error.code == ErrorCode.MAXIMUM_RETRIES_REACH
    assert response.error.detail == "Permanent failure"
    assert logger.warning.call_count == 2
    assert logger.error.call_count == 1
