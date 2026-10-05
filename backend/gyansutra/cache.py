"""Bounded LRU/TTL caches and cancellation-safe concurrent request coalescing."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from cachetools import TTLCache


class ServiceError(Exception):
    def __init__(self, message: str, code: str, attempts: list | None = None):
        super().__init__(message)
        self.code = code
        self.attempts = attempts or []


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
