# mypy: disable-error-code=explicit-any
import asyncio
import inspect
from typing import Any, Callable, Coroutine, TypeGuard, TypeVar, overload

from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def is_coro_function(
    obj: Any,
) -> TypeGuard[Callable[..., Coroutine[Any, Any, T]]]:
    return inspect.iscoroutinefunction(obj)


def is_coro(obj: Any) -> TypeGuard[Coroutine[Any, Any, T]]:
    return inspect.iscoroutine(obj)


@overload
async def run_in_executor(
    obj: Coroutine[Any, Any, T],
) -> T: ...


@overload
async def run_in_executor(
    obj: Callable[P, Coroutine[Any, Any, T]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T: ...


@overload
async def run_in_executor(
    obj: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T: ...


async def run_in_executor(
    obj: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    if is_coro_function(obj):
        return await obj(*args, **kwargs)

    if is_coro(obj):
        return await obj

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: obj(*args, **kwargs),
    )
