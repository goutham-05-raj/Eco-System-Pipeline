import pytest
from datetime import datetime, timezone, timedelta
from src.validation.freshness import is_fresh

def test_freshness_valid():
    now = datetime.now(timezone.utc)
    # 2 hours ago
    assert is_fresh(now - timedelta(hours=2), 24) is True
    # Almost 24 hours ago (allow microsecond execution delay)
    assert is_fresh(now - timedelta(hours=23, minutes=59), 24) is True

def test_freshness_stale():
    now = datetime.now(timezone.utc)
    # 25 hours ago
    assert is_fresh(now - timedelta(hours=25), 24) is False

def test_freshness_future():
    now = datetime.now(timezone.utc)
    # 1 hour in the future (exceeds clock skew)
    assert is_fresh(now + timedelta(hours=1), 24) is False

def test_freshness_none():
    assert is_fresh(None, 24) is False
