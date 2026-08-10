from __future__ import annotations
from typing import Optional
from sqlalchemy import String, Integer, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin


class Startup(Base, TimestampMixin):
    __tablename__ = "startups"
    __table_args__ = (UniqueConstraint("content_id", name="uq_startup_content_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_name: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_name: Mapped[Optional[str]] = mapped_column(Text)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    domain: Mapped[Optional[str]] = mapped_column(String(255))
    resolution_status: Mapped[str] = mapped_column(String(20), default="UNRESOLVED")
    matching_method: Mapped[Optional[str]] = mapped_column(String(30))
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    run_id: Mapped[Optional[str]] = mapped_column(String(30))
    schema_version: Mapped[str] = mapped_column(String(10), default="1.0")
