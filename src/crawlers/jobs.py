from __future__ import annotations
import json
from bs4 import BeautifulSoup
from src.crawlers.http_client import HttpClient
from src.utils.hashing import content_id_from_url
from src.utils.urls import normalise_url
from src.config.logging import get_logger

log = get_logger("jobs")


class AIJobsBoardCrawler:
    """Crawls aijobs.net listings."""

    BASE = "https://aijobs.net"

    async def crawl(self, max_pages: int = 30) -> list[dict]:
        results = []
        async with HttpClient() as client:
            for page in range(1, max_pages + 1):
                url = f"{self.BASE}/?page={page}"
                try:
                    resp = await client.get(url, rps=1.0, source_name="aijobs")
                    if resp.status != 200:
                        break
                    soup = BeautifulSoup(resp.text, "lxml")
                    jobs = (
                        soup.select("article.job")
                        or soup.select(".job-listing")
                        or soup.select("li[data-job-id]")
                        or soup.select(".job-card")
                    )
                    if not jobs:
                        break
                    for job in jobs:
                        title_elem = job.find(["h2", "h3", "h4"])
                        title = title_elem.get_text(strip=True) if title_elem else ""
                        if not title:
                            continue
                        company_elem = job.select_one(".company-name, .employer, .company")
                        company = (
                            company_elem.get_text(strip=True)
                            if company_elem
                            else None
                        )
                        link = job.find("a", href=True)
                        href = link["href"] if link else ""
                        if not href.startswith("http"):
                            href = f"{self.BASE}{href}"
                        source_url = normalise_url(href)
                        is_remote = "remote" in job.get_text().lower()
                        results.append(
                            {
                                "title": title,
                                "company": company,
                                "source_name": "aijobs",
                                "source_url": source_url,
                                "content_id": content_id_from_url(source_url),
                                "is_remote": is_remote,
                                "published_raw": "",
                            }
                        )
                except Exception as exc:
                    log.error("aijobs_error", page=page, error=str(exc))
                    break
        return results


class HNWhoIsHiringCrawler:
    """
    Fetches AI-related job posts from Hacker News via Algolia search API.
    Uses JSON API — no HTML scraping needed.
    """

    API = "https://hn.algolia.com/api/v1/search_by_date"

    async def crawl(self, max_items: int = 200) -> list[dict]:
        url = (
            f"{self.API}?query=AI+OR+ML+OR+LLM+engineer"
            f"&tags=job&hitsPerPage={max_items}"
        )
        try:
            async with HttpClient() as client:
                resp = await client.get(url, rps=2.0, source_name="hn_who_is_hiring")
                if resp.status != 200:
                    return []
                data = json.loads(resp.text)
        except Exception as exc:
            log.error("hn_error", error=str(exc))
            return []

        results = []
        for hit in data.get("hits", []):
            story_id = hit.get("objectID", "")
            if not story_id:
                continue
            hn_url = f"https://news.ycombinator.com/item?id={story_id}"
            norm = normalise_url(hn_url)
            title = (
                hit.get("title")
                or (hit.get("comment_text", "") or "")[:100]
            ).strip()
            if not title:
                continue
            results.append(
                {
                    "title": title,
                    "company": None,
                    "source_name": "hn_who_is_hiring",
                    "source_url": norm,
                    "content_id": content_id_from_url(norm),
                    "is_remote": "remote" in title.lower(),
                    "published_raw": hit.get("created_at", ""),
                }
            )
        log.info("hn_fetched", count=len(results))
        return results


class RemoteOKCrawler:
    """
    Crawls RemoteOK via their JSON API endpoint.
    """

    API = "https://remoteok.com/api?tag=ai"

    async def crawl(self, max_items: int = 200) -> list[dict]:
        try:
            async with HttpClient() as client:
                resp = await client.get(self.API, rps=0.5, source_name="remoteok")
                if resp.status != 200:
                    return []
                data = json.loads(resp.text)
        except Exception as exc:
            log.error("remoteok_error", error=str(exc))
            return []

        results = []
        for item in data:
            if not isinstance(item, dict):
                continue
            url = item.get("url", "")
            if not url or not url.startswith("http"):
                continue
            title = item.get("position", "").strip()
            if not title:
                continue
            norm = normalise_url(url)
            results.append(
                {
                    "title": title,
                    "company": item.get("company") or None,
                    "source_name": "remoteok",
                    "source_url": norm,
                    "content_id": content_id_from_url(norm),
                    "is_remote": True,
                    "published_raw": item.get("date", ""),
                }
            )
            if len(results) >= max_items:
                break
        log.info("remoteok_fetched", count=len(results))
        return results


class JobsCrawler:
    async def crawl_all(self) -> list[dict]:
        all_jobs: list[dict] = []

        aijobs = AIJobsBoardCrawler()
        all_jobs.extend(await aijobs.crawl())

        hn = HNWhoIsHiringCrawler()
        all_jobs.extend(await hn.crawl())

        remoteok = RemoteOKCrawler()
        all_jobs.extend(await remoteok.crawl())

        # Deduplicate
        seen: set[str] = set()
        deduped = []
        for item in all_jobs:
            cid = item.get("content_id", "")
            if cid and cid not in seen:
                seen.add(cid)
                deduped.append(item)
        return deduped
