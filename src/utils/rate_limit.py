from __future__ import annotations
import asyncio
import time
from collections import defaultdict


class RateLimiter:
    """
    Per-domain token-bucket rate limiter.

    Usage:
        await rate_limiter.acquire("arxiv.org", rps=3.0)
    """

    def __init__(self) -> None:
        self._last_call: dict[str, float] = defaultdict(float)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def acquire(self, domain: str, rps: float) -> None:
        """Block until the domain rate allows the next request."""
        if rps <= 0:
            return
        async with self._locks[domain]:
            min_interval = 1.0 / rps
            now = time.monotonic()
            elapsed = now - self._last_call[domain]
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_call[domain] = time.monotonic()


# Singleton — shared across all crawlers in one process
rate_limiter = RateLimiter()
