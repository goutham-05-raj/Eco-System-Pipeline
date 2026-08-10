from __future__ import annotations
import asyncio
import random
from typing import Callable, Awaitable, TypeVar

T = TypeVar("T")


async def with_llm_retry(
    fn: Callable[[], Awaitable[T]],
    max_retries: int = 4,
    base_backoff: float = 1.0,
) -> T:
    """
    Retry an async callable with exponential backoff + jitter.

    attempt 1 → base_backoff * 1 + jitter
    attempt 2 → base_backoff * 2 + jitter
    attempt 3 → base_backoff * 4 + jitter
    ...
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return await fn()
        except Exception as exc:
            last_exc = exc
            if attempt == max_retries:
                break
            backoff = base_backoff * (2 ** (attempt - 1)) + random.uniform(0, 1)
            await asyncio.sleep(backoff)
    raise last_exc  # type: ignore[misc]
