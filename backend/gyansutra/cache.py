"""Bounded LRU/TTL caches and cancellation-safe concurrent request coalescing."""

import asyncio
import time
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from cachetools import TTLCache


class ServiceError(Exception):
    def __init__(self, message: str, code: str, attempts: list | None = None):
        super().__init__(message)
        self.code = code
        self.attempts = attempts or []


class CapacityBudget:
    """Bound both active work and waiting callers; release on every exit path."""

    def __init__(self, active, queued, timeout, code):
        self.semaphore = asyncio.Semaphore(active)
        self.max_queued, self.timeout, self.code = queued, timeout, code
        self.waiting = 0

    @asynccontextmanager
    async def slot(self):
        started = time.monotonic()
        if self.semaphore.locked() and (self.waiting >= self.max_queued or not self.timeout):
            raise ServiceError("Sarathi capacity is busy. Please try again shortly.", self.code)
        if not self.semaphore.locked():
            # Reserve without deferring to another task; burst admission is atomic.
            await self.semaphore.acquire()
        else:
            self.waiting += 1
            try:
                await asyncio.wait_for(self.semaphore.acquire(), self.timeout)
            except TimeoutError as error:
                raise ServiceError(
                    "Sarathi capacity is busy. Please try again shortly.", self.code
                ) from error
            finally:
                self.waiting -= 1
        try:
            yield round((time.monotonic() - started) * 1000)
        finally:
            self.semaphore.release()


class SingleFlight:
    def __init__(self) -> None:
        self.pending: dict[str, asyncio.Task] = {}

    async def run(self, key: str, factory: Callable[[], Awaitable[Any]]) -> Any:
        if key not in self.pending:
            task = asyncio.create_task(factory())
            self.pending[key] = task

            def done(completed: asyncio.Task) -> None:
                self.pending.pop(key, None)
                if not completed.cancelled():
                    completed.exception()  # Observe failures even if all callers disconnected.

            task.add_done_callback(done)
        return await asyncio.shield(self.pending[key])

    async def close(self) -> None:
        tasks = list(self.pending.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


__all__ = ["ServiceError", "SingleFlight", "TTLCache"]
