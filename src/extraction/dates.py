from __future__ import annotations
import json
import re
from datetime import datetime, timezone, timedelta
from typing import Optional
from bs4 import BeautifulSoup
import dateparser


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _try_dateparser(text: str) -> Optional[datetime]:
    if not text or len(text.strip()) < 4:
        return None
    try:
        dt = dateparser.parse(
            text,
            settings={
                "RETURN_AS_TIMEZONE_AWARE": True,
                "TO_TIMEZONE": "UTC",
                "PREFER_DAY_OF_MONTH": "first",
            },
        )
        return dt
    except Exception:
        return None


def parse_relative_date(text: str) -> Optional[datetime]:
    """
    Parse relative date strings:
      '2 hours ago', '45 minutes ago', 'Yesterday', 'Today', 'just now'
    """
    text = text.strip().lower()
    now = datetime.now(timezone.utc)

    if text in ("today", "just now", "moments ago", "now"):
        return now
    if text == "yesterday":
        return now - timedelta(hours=24)

    match = re.match(r"(\d+)\s*(second|minute|hour|day|week)s?\s+ago", text)
    if match:
        qty = int(match.group(1))
        unit = match.group(2)
        deltas = {
            "second": timedelta(seconds=qty),
            "minute": timedelta(minutes=qty),
            "hour": timedelta(hours=qty),
            "day": timedelta(days=qty),
            "week": timedelta(weeks=qty),
        }
        return now - deltas[unit]
    return None


def extract_date(html: str, metadata: dict, fallback_raw: str = "") -> dict:
    """
    Priority-ordered date extraction.
    Returns: {published_at, method, confidence}

    Priority:
    1. JSON-LD datePublished
    2. article:published_time meta
    3. OpenGraph og:updated_time / DC.date
    4. <time datetime="">
    5. ISO pattern in body text
    6. Relative date in fallback_raw
    7. dateparser on fallback_raw
    """
    if html:
        soup = BeautifulSoup(html, "lxml")

        # 1. JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    data = data[0] if data else {}
                date_str = data.get("datePublished") or data.get("dateCreated")
                if date_str:
                    dt = _try_dateparser(date_str)
                    if dt:
                        return {
                            "published_at": _to_utc(dt),
                            "method": "json_ld",
                            "confidence": 0.99,
                        }
            except (json.JSONDecodeError, TypeError):
                pass

        # 2. article:published_time
        meta = soup.find("meta", property="article:published_time")
        if not meta:
            meta = soup.find("meta", attrs={"name": "article:published_time"})
        if meta and meta.get("content"):
            dt = _try_dateparser(meta["content"])
            if dt:
                return {
                    "published_at": _to_utc(dt),
                    "method": "article_published_time",
                    "confidence": 0.97,
                }

        # 3. Other meta tags
        for prop_name in ("og:updated_time", "date", "DC.date", "pubdate"):
            m = soup.find("meta", property=prop_name) or soup.find(
                "meta", attrs={"name": prop_name}
            )
            if m and m.get("content"):
                dt = _try_dateparser(m["content"])
                if dt:
                    return {
                        "published_at": _to_utc(dt),
                        "method": "og_meta",
                        "confidence": 0.90,
                    }

        # 4. <time datetime="...">
        time_elem = soup.find("time", datetime=True)
        if time_elem and time_elem.get("datetime"):
            dt = _try_dateparser(time_elem["datetime"])
            if dt:
                return {
                    "published_at": _to_utc(dt),
                    "method": "time_element",
                    "confidence": 0.95,
                }

    # 5. ISO pattern in text (body or fallback)
    text_to_search = fallback_raw
    if html:
        try:
            text_to_search = BeautifulSoup(html, "lxml").get_text(" ")
        except Exception:
            pass
    
    iso_match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", text_to_search)
    if iso_match:
        dt = _try_dateparser(iso_match.group(0))
        if dt:
            return {
                "published_at": _to_utc(dt),
                "method": "iso_in_body",
                "confidence": 0.85,
            }

    # 6. Relative date in fallback_raw
    if fallback_raw:
        rel_dt = parse_relative_date(fallback_raw)
        if rel_dt:
            return {
                "published_at": rel_dt,
                "method": "relative_date",
                "confidence": 0.75,
            }

        # 7. dateparser on raw
        dt = _try_dateparser(fallback_raw)
        if dt:
            return {
                "published_at": _to_utc(dt),
                "method": "fallback_raw_dateparser",
                "confidence": 0.70,
            }

    return {"published_at": None, "method": "none", "confidence": 0.0}
