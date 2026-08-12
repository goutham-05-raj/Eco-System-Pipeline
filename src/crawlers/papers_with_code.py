from __future__ import annotations
import re
import json
from typing import Optional
from src.crawlers.http_client import HttpClient
from src.config.logging import get_logger

log = get_logger("papers_with_code")

PWC_API = "https://paperswithcode.com/api/v1/papers/"


def extract_arxiv_id(url: str) -> Optional[str]:
    """Pull the bare arXiv ID (e.g. '2401.00001') from an arXiv URL."""
    match = re.search(r"arxiv\.org/abs/([0-9]+\.[0-9]+)", url)
    if match:
        return match.group(1)
    return None


class PapersWithCodeCrawler:
    """
    Correlates arXiv papers with Papers With Code to discover GitHub repos.
    Uses the official PWC REST API — no scraping.
    """

    def _extract_github_url(self, api_response: dict) -> Optional[str]:
        results = api_response.get("results", [])
        if results:
            gh = results[0].get("github_url")
            return gh if gh else None
        return None

    async def get_github_url_for_paper(
        self, arxiv_id: str, client: HttpClient
    ) -> Optional[str]:
        url = f"{PWC_API}?arxiv_id={arxiv_id}"
        try:
            resp = await client.get(url, rps=2.0, source_name="papers_with_code")
            if resp.status == 200 and resp.text and resp.text.strip().startswith("{"):
                data = json.loads(resp.text)
                return self._extract_github_url(data)
        except Exception as exc:
            log.warning("pwc_error", arxiv_id=arxiv_id, error=str(exc))
        return None

    async def enrich(self, papers: list[dict]) -> list[dict]:
        """
        For each paper, attempt to find its GitHub URL via PWC API.
        Sets github_url = None when no repo is found — never guesses.
        """
        async with HttpClient() as client:
            for paper in papers:
                arxiv_id = extract_arxiv_id(paper.get("source_url", ""))
                if arxiv_id:
                    github_url = await self.get_github_url_for_paper(
                        arxiv_id, client
                    )
                    paper["github_url"] = github_url
                else:
                    paper["github_url"] = None
        return papers
