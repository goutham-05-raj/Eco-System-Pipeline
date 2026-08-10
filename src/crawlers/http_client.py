from __future__ import annotations
import asyncio
import random
from dataclasses import dataclass
from typing import Optional
import aiohttp
from urllib.parse import urlparse
from src.config.logging import get_logger
from src.utils.rate_limit import rate_limiter

log = get_logger("http_client")

RETRYABLE_STATUS = {429, 500, 502, 503, 504}
NON_RETRYABLE_STATUS = {400, 401, 403, 404, 410, 422}

DEFAULT_HEADERS = {
    "User-Agent": (
        "GraphOneBot/1.0 (+https://github.com/graphone/intelligence-pipeline; "
        "research crawler; contact: research@example.com)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class HttpResponse:
    url: str
    status: int
    text: str
    headers: dict


class HttpClient:
    """
    Async HTTP client with:
    - Per-domain rate limiting
    - Exponential backoff + jitter on 429/5xx
    - Retry-After header respect
    - Non-retryable 4xx fast-fail
    """

    def __init__(
        self,
        max_retries: int = 4,
        base_backoff: float = 1.0,
        timeout_sec: float = 30.0,
    ) -> None:
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.timeout = aiohttp.ClientTimeout(total=timeout_sec)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "HttpClient":
        self._session = aiohttp.ClientSession(
            headers=DEFAULT_HEADERS,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, *_) -> None:
        if self._session:
            await self._session.close()

    async def get(
        self,
        url: str,
        rps: float = 1.0,
        source_name: str = "unknown",
        **kwargs,
    ) -> HttpResponse:
        domain = urlparse(url).netloc
        for attempt in range(1, self.max_retries + 1):
            await rate_limiter.acquire(domain, rps)
            try:
                async with self._session.get(url, **kwargs) as resp:
                    text = await resp.text(errors="replace")
                    headers = dict(resp.headers)

                    if resp.status in NON_RETRYABLE_STATUS:
                        log.warning(
                            "non_retryable",
                            url=url,
                            status=resp.status,
                            source=source_name,
                        )
                        return HttpResponse(url, resp.status, text, headers)

                    if resp.status in RETRYABLE_STATUS:
                        retry_after = float(headers.get("Retry-After", 0) or 0)
                        backoff = max(
                            retry_after,
                            self.base_backoff * (2 ** (attempt - 1))
                            + random.uniform(0, 1),
                        )
                        log.warning(
                            "retryable_error",
                            url=url,
                            status=resp.status,
                            attempt=attempt,
                            backoff=round(backoff, 2),
                            source=source_name,
                        )
                        if attempt < self.max_retries:
                            await asyncio.sleep(backoff)
                            continue

                    return HttpResponse(url, resp.status, text, headers)

            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                backoff = (
                    self.base_backoff * (2 ** (attempt - 1)) + random.uniform(0, 1)
                )
                log.warning(
                    "request_error",
                    url=url,
                    error=str(exc),
                    attempt=attempt,
                    backoff=round(backoff, 2),
                    source=source_name,
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(backoff)
                else:
                    raise

        raise RuntimeError(f"Exhausted {self.max_retries} retries for {url}")
