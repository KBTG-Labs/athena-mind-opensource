import pytest
import asyncio

from unittest.mock import patch
from typing import Optional, Awaitable, List

from common.decorator.worker import detach_async_worker


class TestWorker:
    @detach_async_worker(workers=2)
    async def __process_messages(self, message: str) -> Awaitable[str]:
        await asyncio.sleep(0.01)
        return f"Processed: {message}"

    async def generate_batch_responses_async(self, messages: List[str]) -> List[str]:
        responses = []
        async for response in self.__process_messages(messages):
            responses.append(response)
        return responses
    

class DynamicWorkerTest:
    def __init__(self, request_workers: Optional[int]):
        self.request_workers = request_workers
    
    @detach_async_worker()
    async def __process_messages(self, message: str) -> Awaitable[str]:
        await asyncio.sleep(0.01)
        return f"Processed: {message}"

    async def generate_batch_responses_async(self, messages: List[str]) -> List[str]:
        responses = []
        async for response in self.__process_messages(messages):
            responses.append(response)
        return responses


@pytest.mark.asyncio
@pytest.mark.worker_decorator
async def test_detach_async_worker():
    message_count = 5
    instance = TestWorker()
    messages = [f"message {i}" for i in range(message_count)]
    expected_results = [f"Processed: message {i}" for i in range(message_count)]
    expected_async_gather_calls = 3

    with patch('asyncio.gather', wraps=asyncio.gather) as mock_gather:
        results = await instance.generate_batch_responses_async(messages)

        assert results == expected_results
        assert mock_gather.call_count == expected_async_gather_calls # With 5 messages and workers=2, we expect 3 calls: [2, 2, 1]



@pytest.mark.asyncio
@pytest.mark.worker_decorator
async def test_dynamic_worker_count():
    message_count, worker_count = 5, 4
    instance = DynamicWorkerTest(request_workers=worker_count)
    messages = [f"message {i}" for i in range(message_count)]
    expected_results = [f"Processed: message {i}" for i in range(message_count)]
    expected_async_gather_calls = 2

    with patch('asyncio.gather', wraps=asyncio.gather) as mock_gather:
        results = await instance.generate_batch_responses_async(messages)

        assert results == expected_results
        assert mock_gather.call_count == expected_async_gather_calls # With 5 messages and workers=4, we expect 2 calls: [4, 1]


@pytest.mark.asyncio
@pytest.mark.worker_decorator
async def test_dynamic_worker_count():
    message_count = 5
    instance = DynamicWorkerTest(request_workers=None)
    messages = [f"message {i}" for i in range(message_count)]
    expected_results = [f"Processed: message {i}" for i in range(message_count)]
    expected_async_gather_calls = 5

    with patch('asyncio.gather', wraps=asyncio.gather) as mock_gather:
        results = await instance.generate_batch_responses_async(messages)

        assert results == expected_results
        assert mock_gather.call_count == expected_async_gather_calls # With 5 messages and workers=1, we expect 5 calls: [1, 1, 1, 1, 1]
