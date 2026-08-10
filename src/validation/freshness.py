from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional


def is_fresh(
    published_at: Optional[datetime],
    freshness_hours: int = 24,
    clock_skew_minutes: int = 5,
) -> bool:
    """
    Return True if published_at is within the freshness window.

    Rules:
    - None → False (unknown date cannot be verified fresh)
    - Future timestamp > clock_skew_minutes → False (invalid)
    - Age > freshness_hours → False (stale)
    - Otherwise → True
    """
    if published_at is None:
        return False
    now = datetime.now(timezone.utc)
    # Reject timestamps too far in the future
    if published_at > now + timedelta(minutes=clock_skew_minutes):
        return False
    age_seconds = (now - published_at).total_seconds()
    return age_seconds <= freshness_hours * 3600
