from __future__ import annotations
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional
from src.crawlers.http_client import HttpClient
from src.utils.hashing import content_id_from_url
from src.utils.urls import normalise_url
from src.config.logging import get_logger

log = get_logger("arxiv")

ATOM_NS = "http://www.w3.org/2005/Atom"
ARXIV_API = "https://export.arxiv.org/api/query"


class ArxivCrawler:
    """
    Fetches AI research papers from the arXiv Atom API.
    Deterministic extraction — no LLM involved.
    """

    def _parse_feed(self, xml_text: str) -> list[dict]:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            log.error("arxiv_parse_error", error=str(exc))
            return []

        papers = []
        for entry in root.findall(f"{{{ATOM_NS}}}entry"):
            id_elem = entry.find(f"{{{ATOM_NS}}}id")
            if id_elem is None or not id_elem.text:
                continue

            raw_url = id_elem.text.strip()
            # Strip version suffix (e.g. v2) → stable canonical
            base_url = raw_url
            last_seg = raw_url.rsplit("/", 1)[-1]
            if "v" in last_seg and last_seg.split("v")[-1].isdigit():
                base_url = raw_url.rsplit("v", 1)[0]
            canonical = normalise_url(base_url)

            title_elem = entry.find(f"{{{ATOM_NS}}}title")
            title = (
                (title_elem.text or "").strip().replace("\n", " ")
                if title_elem is not None
                else ""
            )
            if not title:
                continue

            authors = [
                a.find(f"{{{ATOM_NS}}}name").text.strip()
                for a in entry.findall(f"{{{ATOM_NS}}}author")
                if a.find(f"{{{ATOM_NS}}}name") is not None
                and a.find(f"{{{ATOM_NS}}}name").text
            ]

            pub_elem = entry.find(f"{{{ATOM_NS}}}published")
            published_at: Optional[datetime] = None
            date_method = "arxiv_api"
            date_confidence = 0.99
            if pub_elem is not None and pub_elem.text:
                try:
                    published_at = datetime.fromisoformat(
                        pub_elem.text.strip().replace("Z", "+00:00")
                    )
                except ValueError:
                    published_at = None
                    date_confidence = 0.0

            papers.append(
                {
                    "title": title,
                    "authors": authors,
                    "source_url": canonical,
                    "published_at": published_at,
                    "content_id": content_id_from_url(canonical),
                    "source_name": "arxiv",
                    "date_extraction_method": date_method,
                    "date_confidence": date_confidence,
                    "github_url": None,
                    "github_stars": None,
                }
            )
        return papers

    async def crawl(
        self,
        categories: list[str] | None = None,
        max_results: int = 1000,
        start: int = 0,
    ) -> list[dict]:
        cats = categories or ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "stat.ML"]
        search_query = "+OR+".join(f"cat:{c}" for c in cats)
        all_papers: list[dict] = []
        batch_size = 100

        async with HttpClient() as client:
            for offset in range(start, start + max_results, batch_size):
                remaining = min(batch_size, max_results - len(all_papers))
                if remaining <= 0:
                    break
                url = (
                    f"{ARXIV_API}?search_query={search_query}"
                    f"&start={offset}&max_results={remaining}"
                    f"&sortBy=submittedDate&sortOrder=descending"
                )
                try:
                    resp = await client.get(url, rps=3.0, source_name="arxiv")
                    if resp.status == 200:
                        batch = self._parse_feed(resp.text)
                        all_papers.extend(batch)
                        log.info(
                            "arxiv_batch",
                            offset=offset,
                            fetched=len(batch),
                            total=len(all_papers),
                        )
                        if len(batch) < remaining:
                            break  # API returned fewer than requested → done
                    else:
                        log.warning(
                            "arxiv_bad_status", status=resp.status, url=url
                        )
                        break
                except Exception as exc:
                    log.error("arxiv_error", error=str(exc), offset=offset)
                    break

        return all_papers
