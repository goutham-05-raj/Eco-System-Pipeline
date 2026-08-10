from __future__ import annotations
import feedparser
from src.crawlers.http_client import HttpClient
from src.utils.hashing import content_id_from_url
from src.utils.urls import normalise_url
from src.config.logging import get_logger

log = get_logger("news")

RSS_FEEDS: dict[str, str] = {
    "techcrunch_ai": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "venturebeat_ai": "https://venturebeat.com/category/ai/feed/",
    "mit_news_ai": "https://news.mit.edu/rss/topic/artificial-intelligence",
    "theaibeat": "https://theaibeat.com/feed/",
    "deepmind_blog": "https://deepmind.google/blog/rss.xml",
    "kdnuggets": "https://www.kdnuggets.com/feed",
    "artificial_intelligence_news": "https://www.artificialintelligence-news.com/feed/",
    "google_ai_blog": "https://blog.research.google/feeds/posts/default?alt=rss",
    "marktechpost": "https://www.marktechpost.com/feed/",
}


class RSSNewsCrawler:
    """Fetches news items from RSS feeds — machine-readable publication dates."""

    async def crawl_feed(
        self, source_name: str, feed_url: str, rps: float = 1.0
    ) -> list[dict]:
        try:
            async with HttpClient() as client:
                resp = await client.get(feed_url, rps=rps, source_name=source_name)
                if resp.status != 200:
                    log.warning(
                        "rss_bad_status", source=source_name, status=resp.status
                    )
                    return []
            feed = feedparser.parse(resp.text)
        except Exception as exc:
            log.error("rss_error", source=source_name, error=str(exc))
            return []

        results = []
        for entry in feed.entries:
            url = entry.get("link", "")
            if not url:
                continue
            title = entry.get("title", "").strip()
            if not title:
                continue
            norm = normalise_url(url)
            results.append(
                {
                    "title": title,
                    "source_url": norm,
                    "source_name": source_name,
                    "content_id": content_id_from_url(norm),
                    # 'published' from RSS feeds is often well-structured
                    "raw_published": entry.get("published", ""),
                    "summary": entry.get("summary", "")[:500],
                }
            )
        log.info("rss_fetched", source=source_name, count=len(results))
        return results


class NewsCrawler:
    async def crawl_all(self) -> list[dict]:
        crawler = RSSNewsCrawler()
        all_news: list[dict] = []
        for source_name, feed_url in RSS_FEEDS.items():
            items = await crawler.crawl_feed(source_name, feed_url)
            all_news.extend(items)
        return all_news
