from __future__ import annotations
import re
from typing import Optional


def extract_pricing_heuristic(text: str) -> Optional[str]:
    """Extract pricing model heuristically from product text/title."""
    if not text:
        return None
    lower = text.lower()
    if "open source" in lower or "opensource" in lower or "free & open" in lower:
        return "FREE"
    if "freemium" in lower:
        return "FREEMIUM"
    if "enterprise" in lower:
        return "ENTERPRISE"
    if re.search(r"\bfree\b", lower):
        return "FREE"
    if re.search(r"\b(paid|subscription|\$\d+)\b", lower):
        return "PAID"
    return None
