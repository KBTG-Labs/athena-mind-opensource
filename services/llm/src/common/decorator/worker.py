import asyncio

from typing import List, AsyncIterator, Callable, TypeVar, Optional

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

DEFAULT_WORKER = 1


def detach_async_worker(workers: Optional[int] = None) -> Callable:
    def decorator(func: Callable[[object, TInput], TOutput]) -> Callable[[object, List[TInput]], AsyncIterator[TOutput]]:
        async def wrapper(self, messages: List[TInput]) -> AsyncIterator[TOutput]:
            count = workers or getattr(self, 'request_workers') or \
                DEFAULT_WORKER
            for worker_count in range(0, len(messages), count):
                batch = messages[worker_count:worker_count + count]
                results = await asyncio.gather(*(func(self, message) for message in batch))
                for result in results:
                    yield result
        return wrapper
    return decorator

