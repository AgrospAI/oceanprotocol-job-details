import asyncio
from typing import Coroutine, TypeVar

T = TypeVar("T")


def run_in_executor(coro: Coroutine[None, None, T]) -> T:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)
