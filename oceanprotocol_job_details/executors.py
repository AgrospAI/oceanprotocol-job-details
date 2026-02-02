import asyncio
import inspect
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar("T")


def run_in_executor(obj: Callable[..., Any] | Coroutine[Any, Any, T]) -> T:
    if callable(obj) and not inspect.iscoroutinefunction(obj):
        return obj()

    if inspect.iscoroutinefunction(obj):
        obj = obj()

    if not inspect.iscoroutine(obj):
        return obj

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(obj)

    future = asyncio.run_coroutine_threadsafe(obj, loop)
    return future.result()
