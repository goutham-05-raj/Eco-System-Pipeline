from __future__ import annotations
import asyncio
from typing import Callable, Awaitable
from src.config.logging import get_logger

log = get_logger("pipeline_worker")


class WorkerPool:
    """
    Bounded concurrency execution pool using asyncio.Queue.
    Ensures we don't overwhelm local resources or hit LLM API limits too fast,
    while still keeping throughput high.
    """

    def __init__(self, concurrency: int = 10) -> None:
        self.concurrency = concurrency
        self.queue: asyncio.Queue = asyncio.Queue()
        self.workers: list[asyncio.Task] = []
        self._is_running = False

    async def _worker(self, worker_id: int) -> None:
        log.debug("worker_started", worker_id=worker_id)
        while self._is_running:
            try:
                task_fn = await self.queue.get()
                try:
                    await task_fn()
                except Exception as exc:
                    log.error("worker_task_failed", worker_id=worker_id, error=str(exc))
                finally:
                    self.queue.task_done()
            except asyncio.CancelledError:
                break
        log.debug("worker_stopped", worker_id=worker_id)

    async def start(self) -> None:
        self._is_running = True
        for i in range(self.concurrency):
            task = asyncio.create_task(self._worker(i))
            self.workers.append(task)
        log.info("pool_started", concurrency=self.concurrency)

    async def submit(self, task_fn: Callable[[], Awaitable[None]]) -> None:
        await self.queue.put(task_fn)

    async def join(self) -> None:
        await self.queue.join()
        self._is_running = False
        for w in self.workers:
            w.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        log.info("pool_stopped")
