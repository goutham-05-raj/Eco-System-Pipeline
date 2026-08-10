from __future__ import annotations
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator


class PricingModel(str, Enum):
    FREE = "FREE"
    FREEMIUM = "FREEMIUM"
    PAID = "PAID"
    ENTERPRISE = "ENTERPRISE"


class SchemaBase(BaseModel):
    schema_version: str = "1.0"
    content_id: str
    source_name: str
    source_url: str

    @field_validator("source_url", mode="before")
    @classmethod
    def validate_url(cls, v: object) -> str:
        v = str(v)
        if not v.startswith("http"):
            raise ValueError(f"source_url must start with http: {v!r}")
        return v


class ResearchPaperSchema(SchemaBase):
    title: str
    authors: list[str] = []
    github_url: Optional[str] = None
    github_stars: Optional[int] = None
    published_at: Optional[datetime] = None
    date_extraction_method: Optional[str] = None
    date_confidence: Optional[float] = None

    @field_validator("github_stars", mode="before")
    @classmethod
    def stars_non_negative(cls, v: object) -> Optional[int]:
        if v is not None and int(v) < 0:
            return None
        return v

    @field_validator("title", mode="before")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()


class StartupSchema(SchemaBase):
    raw_name: str
    canonical_name: Optional[str] = None
    employee_count: Optional[int] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    resolution_status: str = "UNRESOLVED"

    @field_validator("employee_count", mode="before")
    @classmethod
    def positive_employees(cls, v: object) -> Optional[int]:
        if v is not None and int(v) <= 0:
            return None
        return v


class ProductSchema(SchemaBase):
    product_name: str
    startup_name: Optional[str] = None
    pricing_model: Optional[PricingModel] = None

    @field_validator("product_name", mode="before")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not str(v).strip():
            raise ValueError("product_name must not be empty")
        return str(v).strip()


class JobSchema(SchemaBase):
    title: str
    company: Optional[str] = None
    role_family: Optional[str] = None
    is_remote: bool = False
    published_at: Optional[datetime] = None
    collected_at: Optional[datetime] = None
    date_extraction_method: Optional[str] = None
    date_confidence: Optional[float] = None


class NewsSchema(SchemaBase):
    title: str
    canonical_url: Optional[str] = None
    published_at: Optional[datetime] = None
    collected_at: Optional[datetime] = None
    date_extraction_method: Optional[str] = None
    date_confidence: Optional[float] = None

    @field_validator("title", mode="before")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not str(v).strip():
            raise ValueError("title must not be empty")
        return str(v).strip()
