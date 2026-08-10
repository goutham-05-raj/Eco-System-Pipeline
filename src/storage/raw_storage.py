from __future__ import annotations
import aiofiles
from datetime import datetime, timezone
from pathlib import Path

RAW_BASE = Path("data/raw")


async def save_raw(
    source: str,
    content_hash: str,
    content: str | bytes,
    extension: str = "html",
) -> str:
    """Persist raw page content and return the storage path."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dir_path = RAW_BASE / source / date_str
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"{content_hash}.{extension}"
    if isinstance(content, bytes):
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(content)
    else:
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(content)
    return str(file_path)


# Production note: replace save_raw with an S3-compatible abstraction.
# The database stores raw_storage_path; the path prefix switches from
# "data/raw/" to "s3://bucket/raw/" without touching crawler logic.
