import inspect
import logging
import time
from functools import wraps
from typing import Awaitable, Callable, Tuple, TypeVar

TOutput = TypeVar('TOutput')

def retry(max_retries: int, delay: int, backoff: int, logger: logging.Logger, exceptions: Tuple[Exception] = (Exception, ), fallback_response=None):
    def decorator(fn: Callable[..., TOutput | Awaitable[TOutput]]):
        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            attempt = 0
            _delay = delay
            while attempt < max_retries:
                try:
                    result = await fn(*args, **kwargs)
                    break
                except exceptions as e:
                    attempt += 1
                    if attempt < max_retries:
                        retries_count = f"{attempt+1}/{max_retries}"
                        logger.warning({
                            "message": f"Error while processing, retrying attempt {retries_count} in {_delay} seconds",
                            "error": str(e),
                        })
                        time.sleep(_delay)
                        _delay *= backoff
                    else:
                        result = fallback_response
                        logger.error({
                            "message": "Retrying attempt exceeded",
                            "error": str(e),
                        })

            return result

        @wraps(fn)
        def sync_wrapper(*args, **kwargs) -> TOutput:
            attempt = 0
            _delay = delay
            while attempt < max_retries:
                try:
                    result = fn(*args, **kwargs)
                    break
                except exceptions as e:
                    attempt += 1
                    if attempt < max_retries:
                        retries_count = f"{attempt+1}/{max_retries}"
                        logger.warning({
                            "message": f"Error while processing, retrying attempt {retries_count} in {_delay} seconds",
                            "error": str(e),
                        })
                        time.sleep(_delay)
                        _delay *= backoff
                    else:
                        result = fallback_response
                        logger.error({
                            "message": "Retrying attempt exceeded",
                            "error": str(e),
                        })

            return result

        return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper
    return decorator
