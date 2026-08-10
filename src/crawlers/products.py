from __future__ import annotations
from bs4 import BeautifulSoup
import json
from src.crawlers.http_client import HttpClient
from src.utils.hashing import content_id_from_url
from src.utils.urls import normalise_url
from src.config.logging import get_logger

log = get_logger("products")

PRICING_KEYWORDS: dict[str, list[str]] = {
    "FREE": ["open source", "free forever", "no credit card", "100% free"],
    "FREEMIUM": ["free plan", "free tier", "freemium", "upgrade to pro", "try for free"],
    "PAID": ["per month", "per year", "subscribe", "buy now", "purchase", "$"],
    "ENTERPRISE": ["enterprise", "contact sales", "custom pricing", "talk to us"],
}


def infer_pricing_model(text: str) -> str | None:
    """
    Infer pricing from keyword presence in card text.
    Returns None when confidence is insufficient — never guesses.
    """
    text_lower = text.lower()
    # More specific keywords checked first; ENTERPRISE overrides PAID
    for model in ("ENTERPRISE", "FREE", "FREEMIUM", "PAID"):
        if any(kw in text_lower for kw in PRICING_KEYWORDS[model]):
            return model
    return None


class FuturepediaCrawler:
    BASE = "https://www.futurepedia.io/ai-tools"

    async def crawl(self, max_pages: int = 60) -> list[dict]:
        results = []
        async with HttpClient() as client:
            for page in range(1, max_pages + 1):
                url = f"{self.BASE}?page={page}"
                try:
                    resp = await client.get(url, rps=1.0, source_name="futurepedia")
                    if resp.status != 200:
                        break
                    soup = BeautifulSoup(resp.text, "lxml")
                    cards = (
                        soup.select("article")
                        or soup.select(".tool-card")
                        or soup.select("[data-tool]")
                    )
                    if not cards:
                        break
                    for card in cards:
                        name_elem = card.find(["h2", "h3", "h4"])
                        if not name_elem:
                            continue
                        product_name = name_elem.get_text(strip=True)
                        link = card.find("a", href=True)
                        href = link["href"] if link else ""
                        if not href.startswith("http"):
                            href = f"https://www.futurepedia.io{href}"
                        source_url = normalise_url(href)
                        results.append(
                            {
                                "product_name": product_name,
                                "startup_name": None,
                                "pricing_model": infer_pricing_model(card.get_text(" ")),
                                "source_name": "futurepedia",
                                "source_url": source_url,
                                "content_id": content_id_from_url(source_url),
                            }
                        )
                except Exception as exc:
                    log.error("futurepedia_error", page=page, error=str(exc))
                    break
        return results


class TheresAnAIForThatCrawler:
    BASE = "https://theresanaiforthat.com"

    async def crawl(self, max_pages: int = 60) -> list[dict]:
        results = []
        async with HttpClient() as client:
            for page in range(1, max_pages + 1):
                url = f"{self.BASE}/?page={page}"
                try:
                    resp = await client.get(
                        url, rps=1.0, source_name="theresanaiforthat"
                    )
                    if resp.status != 200:
                        break
                    soup = BeautifulSoup(resp.text, "lxml")
                    cards = (
                        soup.select(".ai_tool")
                        or soup.select(".tool-item")
                        or soup.select("article")
                    )
                    if not cards:
                        break
                    for card in cards:
                        name_elem = card.find(["h2", "h3", "strong"])
                        if not name_elem:
                            continue
                        product_name = name_elem.get_text(strip=True)
                        link = card.find("a", href=True)
                        href = link["href"] if link else ""
                        if not href.startswith("http"):
                            href = f"{self.BASE}{href}"
                        source_url = normalise_url(href)
                        results.append(
                            {
                                "product_name": product_name,
                                "startup_name": None,
                                "pricing_model": infer_pricing_model(card.get_text(" ")),
                                "source_name": "theresanaiforthat",
                                "source_url": source_url,
                                "content_id": content_id_from_url(source_url),
                            }
                        )
                except Exception as exc:
                    log.error("taat_error", page=page, error=str(exc))
                    break
        return results


class HackerNewsProductCrawler:
    BASE = "https://hn.algolia.com/api/v1/search"

    async def crawl(self, max_pages: int = 20) -> list[dict]:
        results = []
        async with HttpClient() as client:
            for page in range(max_pages):
                # Search for 'Show HN AI' to find AI product launches
                url = f"{self.BASE}?query=Show%20HN%20AI&tags=story&page={page}&hitsPerPage=50"
                try:
                    resp = await client.get(url, rps=1.0, source_name="hn_algolia")
                    if resp.status != 200:
                        break
                    
                    data = json.loads(resp.text)
                    hits = data.get("hits", [])
                    if not hits:
                        break
                        
                    for hit in hits:
                        title = hit.get("title", "")
                        url = hit.get("url", "")
                        
                        # Only accept hits that actually have a URL
                        if not url or not url.startswith("http"):
                            url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                            
                        # Clean title
                        if title.startswith("Show HN:"):
                            title = title.replace("Show HN:", "").strip()
                            
                        source_url = normalise_url(url)
                        results.append({
                            "product_name": title[:100],  # keep it reasonable
                            "startup_name": None,
                            "pricing_model": None,  # HN doesn't provide this predictably
                            "source_name": "hacker_news",
                            "source_url": source_url,
                            "content_id": content_id_from_url(source_url),
                        })
                except Exception as exc:
                    log.error("hn_products_error", page=page, error=str(exc))
                    break
        return results

class ProductCrawler:
    async def crawl_all(self, max_per_source: int = 2000) -> list[dict]:
        all_results: list[dict] = []
        pages = min(max_per_source // 10, 60)

        fp = FuturepediaCrawler()
        fp_results = await fp.crawl(max_pages=pages)
        all_results.extend(fp_results)
        log.info("product_source_done", source="futurepedia", count=len(fp_results))

        ta = TheresAnAIForThatCrawler()
        ta_results = await ta.crawl(max_pages=pages)
        all_results.extend(ta_results)
        log.info("product_source_done", source="theresanaiforthat", count=len(ta_results))

        hn = HackerNewsProductCrawler()
        hn_results = await hn.crawl(max_pages=max_per_source // 50)
        all_results.extend(hn_results)
        log.info("product_source_done", source="hacker_news", count=len(hn_results))

        seen: set[str] = set()
        deduped = []
        for item in all_results:
            cid = item.get("content_id", "")
            if cid and cid not in seen:
                seen.add(cid)
                deduped.append(item)
        return deduped
