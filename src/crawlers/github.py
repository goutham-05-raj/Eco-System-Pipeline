from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import Optional
import aiohttp
from src.config.settings import settings
from src.config.logging import get_logger
from src.utils.rate_limit import rate_limiter

log = get_logger("github")

GITHUB_API = "https://api.github.com/repos"


def parse_repo_path(url: str) -> Optional[tuple[str, str]]:
    """Extract (owner, repo) from a GitHub URL. Returns None for non-GitHub URLs."""
    match = re.match(r"https://github\.com/([^/\s]+)/([^/\s]+?)(?:/.*)?$", url.strip())
    if match:
        return match.group(1), match.group(2).rstrip(".git")
    return None


class GitHubClient:
    """
    Fetches repository metrics from the GitHub REST API v3.
    github_stars is ALWAYS from the API — never estimated.
    """

    def __init__(self, token: str | None = None) -> None:
        self.token = token or settings.github_token
        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self._headers["Authorization"] = f"Bearer {self.token}"

    def _null_result(self, repo_url: str) -> dict:
        return {
            "github_url": repo_url,
            "github_stars": None,
            "github_metrics_collected_at": None,
        }

    async def get_stars(self, repo_url: str) -> dict:
        """
        Returns {github_url, github_stars, github_metrics_collected_at}.
        github_stars is None if:
          - URL is not a GitHub URL
          - Repo not found (404)
          - Rate limited (429/403)
          - Any network error
        Never estimates or guesses.
        """
        if not repo_url:
            return self._null_result(repo_url)

        parsed = parse_repo_path(repo_url)
        if parsed is None:
            log.debug("github_not_github_url", url=repo_url)
            return self._null_result(repo_url)

        owner, repo = parsed
        api_url = f"{GITHUB_API}/{owner}/{repo}"

        # Stay under 5000 req/hr (authenticated) = ~1.3/sec; use 0.9 to be safe
        await rate_limiter.acquire("api.github.com", rps=0.9)

        try:
            async with aiohttp.ClientSession(headers=self._headers) as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "github_url": repo_url,
                            "github_stars": data.get("stargazers_count"),
                            "github_metrics_collected_at": datetime.now(
                                timezone.utc
                            ).isoformat(),
                        }
                    elif resp.status in (403, 404):
                        log.warning(
                            "github_not_found",
                            url=repo_url,
                            status=resp.status,
                        )
                        return self._null_result(repo_url)
                    elif resp.status == 429:
                        log.warning("github_rate_limited", url=repo_url)
                        return self._null_result(repo_url)
                    else:
                        log.warning(
                            "github_unexpected",
                            url=repo_url,
                            status=resp.status,
                        )
                        return self._null_result(repo_url)
        except Exception as exc:
            log.error("github_error", url=repo_url, error=str(exc))
            return self._null_result(repo_url)
