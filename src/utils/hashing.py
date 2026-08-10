from __future__ import annotations
import hashlib


def sha256_hex(text: str) -> str:
    """Deterministic SHA-256 hex digest of UTF-8 text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_id_from_url(url: str) -> str:
    """Stable content identity from normalised URL."""
    from src.utils.urls import normalise_url
    return sha256_hex(normalise_url(url))


def content_id_from_url_and_title(url: str, title: str) -> str:
    """Compound identity for cases where URL alone is insufficient."""
    from src.utils.urls import normalise_url
    combined = normalise_url(url) + "|" + title.strip().lower()
    return sha256_hex(combined)
