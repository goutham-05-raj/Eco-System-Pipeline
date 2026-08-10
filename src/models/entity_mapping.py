from __future__ import annotations
from typing import Optional
from sqlalchemy import String, Integer, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin


class EntityMapping(Base, TimestampMixin):
    __tablename__ = "entity_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    raw_name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    canonical_name: Mapped[Optional[str]] = mapped_column(Text)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)   # STARTUP|PRODUCT
    matching_method: Mapped[Optional[str]] = mapped_column(String(30))
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    resolution_status: Mapped[str] = mapped_column(String(20), default="UNRESOLVED")
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    run_id: Mapped[Optional[str]] = mapped_column(String(30))
