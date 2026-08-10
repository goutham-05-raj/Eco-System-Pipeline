from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin


class News(Base, TimestampMixin):
    __tablename__ = "news"
    __table_args__ = (UniqueConstraint("content_id", name="uq_news_content_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[Optional[str]] = mapped_column(Text)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    date_extraction_method: Mapped[Optional[str]] = mapped_column(String(50))
    date_confidence: Mapped[Optional[float]] = mapped_column(Float)
    run_id: Mapped[Optional[str]] = mapped_column(String(30))
    schema_version: Mapped[str] = mapped_column(String(10), default="1.0")
