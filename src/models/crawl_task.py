from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin


class CrawlTask(Base, TimestampMixin):
    __tablename__ = "crawl_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    record_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    content_id: Mapped[Optional[str]] = mapped_column(String(64))
    run_id: Mapped[Optional[str]] = mapped_column(String(30))
    last_attempted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
