import asyncio
import inspect
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar("T")


async def run_in_executor(
    obj: Callable[..., T]
    | Callable[..., Coroutine[Any, Any, T]]
    | Coroutine[Any, Any, T],
    *args,
    **kwargs,
) -> T:
    if inspect.iscoroutinefunction(obj):
        return await obj(*args, **kwargs)

    if inspect.iscoroutine(obj):
        return await obj

    if callable(obj):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, obj, *args, **kwargs)

    return obj
