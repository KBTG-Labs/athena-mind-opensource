import asyncio
import time
import logging
import inspect

from functools import wraps
from typing import Callable, TypeVar, Generic, Awaitable

from common.exception import Error, ErrorCode

TOutput = TypeVar('TOutput')


class GenericResponse(Generic[TOutput]):
    def __init__(self, results: TOutput = None, error: Error = None):
        self.results = results
        self.error = error


def retry(max_retries: int, delay: int, logger: logging.Logger):
    def decorator(fn: Callable[..., TOutput | Awaitable[TOutput]]):
        @wraps(fn)
        async def async_wrapper(*args, **kwargs) -> GenericResponse[TOutput]:
            response = GenericResponse[TOutput]()
            attempt = 0
            while attempt < max_retries:
                try:
                    result = await fn(*args, **kwargs)
                    response.results = result
                    break
                except Exception as e:
                    attempt += 1
                    if attempt < max_retries:
                        retries_count = f"{attempt+1}/{max_retries}"
                        message = f"Error While Processing Message: {e}\nRetrying (Attempt: {retries_count})"
                        logger.warning(message)
                        await asyncio.sleep(delay)
                    else:
                        logger.error("Retrying Attempt Exceeded")
                        response.error = Error(
                            code=ErrorCode.MAXIMUM_RETRIES_REACH,
                            detail=str(e),
                        )
            return response

        @wraps(fn)
        def sync_wrapper(*args, **kwargs) -> GenericResponse[TOutput]:
            response = GenericResponse[TOutput]()
            attempt = 0
            while attempt < max_retries:
                try:
                    result = fn(*args, **kwargs)
                    response.results = result
                    break
                except Exception as e:
                    attempt += 1
                    if attempt < max_retries:
                        retries_count = f"{attempt+1}/{max_retries}"
                        message = f"Error While Processing Message: {e}\nRetrying (Attempt: {retries_count})"
                        logger.warning(message)
                        time.sleep(delay)
                    else:
                        logger.error("Retrying Attempt Exceeded")
                        response.error = Error(
                            code=ErrorCode.MAXIMUM_RETRIES_REACH,
                            detail=str(e),
                        )
            return response

        return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper
    return decorator
