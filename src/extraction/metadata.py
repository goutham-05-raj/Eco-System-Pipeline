from __future__ import annotations
import json
from typing import Any
from bs4 import BeautifulSoup


def extract_metadata(html: str, url: str) -> dict[str, Any]:
    """
    Extract structured metadata from HTML without an LLM:
    - canonical URL
    - OpenGraph tags
    - article:published_time
    - JSON-LD structured data
    """
    soup = BeautifulSoup(html, "lxml")
    meta: dict[str, Any] = {"source_url": url}

    # Canonical URL
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        meta["canonical_url"] = canonical["href"]

    # Meta property / name tags
    og_map = {
        "og:title": "og_title",
        "og:description": "og_description",
        "og:type": "og_type",
        "og:url": "og_url",
        "article:published_time": "article_published_time",
        "article:modified_time": "article_modified_time",
    }
    for tag in soup.find_all("meta"):
        prop = tag.get("property") or tag.get("name", "")
        if prop in og_map:
            meta[og_map[prop]] = tag.get("content", "")

    # JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                data = data[0] if data else {}
            meta["json_ld"] = data
            break
        except (json.JSONDecodeError, TypeError):
            pass

    return meta
