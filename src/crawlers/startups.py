from __future__ import annotations
import json
from bs4 import BeautifulSoup
from src.crawlers.http_client import HttpClient
from src.utils.hashing import content_id_from_url
from src.utils.urls import normalise_url
from src.config.logging import get_logger

log = get_logger("startups")


class YCombinatorCrawler:
    """
    Crawls Y Combinator companies using their public JSON API.
    Only collects fields the API actually returns — never invents data.
    """

    YC_API = "https://api.ycombinator.com/v0.1/companies"

    async def crawl(self, max_pages: int = 20) -> list[dict]:
        results = []
        async with HttpClient() as client:
            for page in range(1, max_pages + 1):
                url = f"{self.YC_API}?page={page}&focus=AI"
                try:
                    resp = await client.get(url, rps=1.0, source_name="ycombinator")
                    if resp.status != 200:
                        log.warning("yc_bad_status", page=page, status=resp.status)
                        break
                    data = json.loads(resp.text)
                    companies = data.get("companies", [])
                    if not companies:
                        break
                    for c in companies:
                        slug = c.get("slug", "")
                        if not slug:
                            continue
                        source_url = normalise_url(
                            f"https://www.ycombinator.com/companies/{slug}"
                        )
                        results.append(
                            {
                                "raw_name": c.get("name", ""),
                                "source_name": "ycombinator",
                                "source_url": source_url,
                                "content_id": content_id_from_url(source_url),
                                "description": c.get("one_liner") or None,
                                "domain": c.get("website") or None,
                                "employee_count": None,  # Not in listing API
                            }
                        )
                    log.info("yc_page", page=page, count=len(companies))
                except Exception as exc:
                    log.error("yc_error", page=page, error=str(exc))
                    break
        return results


class F6SCrawler:
    """
    Crawls F6S AI company listings via HTML parsing.
    Falls back gracefully if selectors change.
    """

    BASE_URL = "https://www.f6s.com/companies/artificial-intelligence/co"

    async def crawl(self, max_pages: int = 50) -> list[dict]:
        results = []
        async with HttpClient() as client:
            for page in range(1, max_pages + 1):
                url = f"{self.BASE_URL}?page={page}"
                try:
                    resp = await client.get(url, rps=1.0, source_name="f6s")
                    if resp.status != 200:
                        break
                    soup = BeautifulSoup(resp.text, "lxml")
                    # Try multiple selector patterns as F6S may change markup
                    cards = (
                        soup.select(".company-name")
                        or soup.select("h3.name")
                        or soup.select(".listing-title")
                        or soup.select("a.company-link")
                    )
                    if not cards:
                        log.info("f6s_no_cards", page=page)
                        break
                    for card in cards:
                        link = card if card.name == "a" else card.find("a")
                        name = (link or card).get_text(strip=True)
                        if not name:
                            continue
                        href = (link.get("href", "") if link else "") or ""
                        if not href.startswith("http"):
                            href = f"https://www.f6s.com{href}"
                        source_url = normalise_url(href)
                        results.append(
                            {
                                "raw_name": name,
                                "source_name": "f6s",
                                "source_url": source_url,
                                "content_id": content_id_from_url(source_url),
                                "employee_count": None,
                                "description": None,
                                "domain": None,
                            }
                        )
                except Exception as exc:
                    log.error("f6s_error", page=page, error=str(exc))
                    break
        return results


class StartupCrawler:
    """Orchestrates multiple startup source crawlers."""

    async def crawl_all(self, max_per_source: int = 2000) -> list[dict]:
        all_results: list[dict] = []

        yc = YCombinatorCrawler()
        yc_pages = min(max_per_source // 10, 30)
        yc_results = await yc.crawl(max_pages=yc_pages)
        all_results.extend(yc_results)
        log.info("startup_source_done", source="ycombinator", count=len(yc_results))

        f6s = F6SCrawler()
        f6s_pages = min(max_per_source // 10, 50)
        f6s_results = await f6s.crawl(max_pages=f6s_pages)
        all_results.extend(f6s_results)
        log.info("startup_source_done", source="f6s", count=len(f6s_results))

        # Deduplicate by content_id
        seen: set[str] = set()
        deduped = []
        for item in all_results:
            cid = item.get("content_id", "")
            if cid and cid not in seen:
                seen.add(cid)
                deduped.append(item)
        log.info(
            "startups_deduped",
            total=len(all_results),
            unique=len(deduped),
        )
        return deduped
