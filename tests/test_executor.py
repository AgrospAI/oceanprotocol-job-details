import asyncio
import time

import pytest

from oceanprotocol_job_details.executors import run_in_executor


def sync_add(x: int, y: int) -> int:
    return x + y


def sync_sleep_and_append(log: list[str], value: str) -> None:
    time.sleep(0.05)
    log.append(value)


async def async_add(x: int, y: int) -> int:
    await asyncio.sleep(0.01)
    return x + y


async def async_sleep_and_append(log: list[str], value: str) -> None:
    await asyncio.sleep(0.01)
    log.append(value)


@pytest.mark.asyncio
async def test_sync_callable_runs_in_executor():
    result = await run_in_executor(sync_add, 2, 3)
    assert result == 5


@pytest.mark.asyncio
async def test_async_callable_runs():
    result = await run_in_executor(async_add, 4, 6)
    assert result == 10


@pytest.mark.asyncio
async def test_coroutine_object_runs():
    coro = async_add(1, 2)
    result = await run_in_executor(coro)
    assert result == 3


@pytest.mark.asyncio
async def test_execution_order_is_preserved():
    log: list[str] = []

    await run_in_executor(sync_sleep_and_append, log, "validate")
    await run_in_executor(async_sleep_and_append, log, "run")
    await run_in_executor(sync_sleep_and_append, log, "save")

    assert log == ["validate", "run", "save"]


@pytest.mark.asyncio
async def test_mixed_sync_and_async_order():
    log: list[str] = []

    await run_in_executor(sync_sleep_and_append, log, "A")
    await run_in_executor(async_sleep_and_append, log, "B")
    await run_in_executor(sync_sleep_and_append, log, "C")

    assert log == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_exception_propagates_from_sync():
    def boom() -> None:
        raise ValueError("sync error")

    with pytest.raises(ValueError, match="sync error"):
        await run_in_executor(boom)


@pytest.mark.asyncio
async def test_exception_propagates_from_async():
    async def boom() -> None:
        raise RuntimeError("async error")

    with pytest.raises(RuntimeError, match="async error"):
        await run_in_executor(boom)
