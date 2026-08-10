import pytest
from datetime import datetime, timezone
from src.extraction.dates import extract_date

def test_extract_date_relative():
    # 2 hours ago
    dt = extract_date("", {}, "2 hours ago")["published_at"]
    assert dt is not None
    assert (datetime.now(timezone.utc) - dt).total_seconds() < 2.5 * 3600

def test_extract_date_iso_fallback():
    raw = "The release happened on 2024-05-10T12:00:00Z."
    dt = extract_date("", {}, raw)["published_at"]
    assert dt is not None
    assert dt.year == 2024
    assert dt.month == 5
