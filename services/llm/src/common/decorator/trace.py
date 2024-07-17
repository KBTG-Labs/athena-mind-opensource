import inspect
from functools import wraps
from typing import Awaitable, Callable, TypeVar

from common.log.log import correlation_id
from common.telemetry import app_telemetry

TOutput = TypeVar('TOutput')

def trace(fn: Callable[..., TOutput | Awaitable[TOutput]]):
    @wraps(fn)
    async def async_wrapper(*args, **kwargs):
        if app_telemetry.enable_telemetry:
            event_name = f"{fn.__module__}.{fn.__name__}"
            tags = {
                "request_id": correlation_id.get(),
            }
            with app_telemetry.tracer.start_as_current_span(
                event_name,
                record_exception=False,
                set_status_on_exception=False,
                attributes=tags,
            ):
                return await fn(*args, **kwargs)
        else:
            return await fn(*args, **kwargs)
        
    @wraps(fn)
    def sync_wrapper(*args, **kwargs):
        if app_telemetry.enable_telemetry:
            event_name = f"{fn.__module__}.{fn.__name__}"
            tags = {
                "request_id": correlation_id.get(),
            }
            with app_telemetry.tracer.start_as_current_span(
                event_name,
                record_exception=False,
                set_status_on_exception=False,
                attributes=tags,
            ):
                return fn(*args, **kwargs)
        else:
            return fn(*args, **kwargs)
    return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper

def trace_with_message_id(fn: Callable[..., TOutput | Awaitable[TOutput]]):
    @wraps(fn)
    async def async_wrapper(self, message):
        if app_telemetry.enable_telemetry:
            event_name = f"{fn.__module__}.{fn.__name__}"
            tags = {
                "request_id": correlation_id.get(),
                "message_id": message.id,
            }
            with app_telemetry.tracer.start_as_current_span(
                event_name,
                record_exception=False,
                set_status_on_exception=False,
                attributes=tags,
            ):
                return await fn(self, message)
        else:
            return await fn(self, message)
        
    @wraps(fn)
    def sync_wrapper(self, message):
        if app_telemetry.enable_telemetry:
            event_name = f"{fn.__module__}.{fn.__name__}"
            tags = {
                "request_id": correlation_id.get(),
                "message_id": message.id,
            }
            with app_telemetry.tracer.start_as_current_span(
                event_name,
                record_exception=False,
                set_status_on_exception=False,
                attributes=tags,
            ):
                return fn(self, message)
        else:
            return fn(self, message)
    return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper