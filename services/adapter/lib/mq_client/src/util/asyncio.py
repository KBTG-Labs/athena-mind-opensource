import asyncio
import threading

from typing import Callable


def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def start_new_thread(fn: Callable[[float], None]):
    loop = asyncio.new_event_loop()
    threading.Thread(target=start_async_loop, args=(loop,)).start()
    asyncio.run_coroutine_threadsafe(fn, loop)
