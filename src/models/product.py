from __future__ import annotations
from typing import Optional
from sqlalchemy import String, Integer, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("content_id", name="uq_product_content_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(Text, nullable=False)
    startup_name: Mapped[Optional[str]] = mapped_column(Text)
    # FREE | FREEMIUM | PAID | ENTERPRISE | None
    pricing_model: Mapped[Optional[str]] = mapped_column(String(20))
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    run_id: Mapped[Optional[str]] = mapped_column(String(30))
    schema_version: Mapped[str] = mapped_column(String(10), default="1.0")
