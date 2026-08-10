from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Text, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("content_id", name="uq_job_content_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    company: Mapped[Optional[str]] = mapped_column(Text)
    role_family: Mapped[Optional[str]] = mapped_column(String(50))
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    date_extraction_method: Mapped[Optional[str]] = mapped_column(String(50))
    date_confidence: Mapped[Optional[float]] = mapped_column(Float)
    run_id: Mapped[Optional[str]] = mapped_column(String(30))
    schema_version: Mapped[str] = mapped_column(String(10), default="1.0")
