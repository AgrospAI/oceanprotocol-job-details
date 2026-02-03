# mypy: disable-error-code=explicit-any
import asyncio
import inspect
from functools import partial
from typing import Any, Callable, Coroutine, TypeGuard, TypeVar, cast

T = TypeVar("T")


def is_coro_function(
    obj: Any,
) -> TypeGuard[Callable[..., Coroutine[Any, Any, T]]]:
    return inspect.iscoroutinefunction(obj)


def is_coro(obj: Any) -> TypeGuard[Coroutine[Any, Any, T]]:
    return inspect.iscoroutine(obj)


async def run_in_executor(
    obj: Callable[..., T]
    | Callable[..., Coroutine[Any, Any, T]]
    | Coroutine[Any, Any, T],
    *args: Any,
    **kwargs: Any,
) -> T:
    if is_coro_function(obj):
        return await obj(*args, **kwargs)

    if is_coro(obj):
        return await obj

    if callable(obj):
        loop = asyncio.get_running_loop()

        # just to comply with mypy
        func = partial(obj, *args, **kwargs)
        return await loop.run_in_executor(None, cast(Callable[[], T], func))

    return cast(T, obj)
