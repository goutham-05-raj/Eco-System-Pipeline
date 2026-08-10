from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.research_paper import ResearchPaper
from src.models.startup import Startup
from src.models.product import Product
from src.models.job import Job
from src.models.news import News
from src.models.entity_mapping import EntityMapping
from src.config.logging import get_logger

log = get_logger("repositories")


class ResearchPaperRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, data: dict[str, Any]) -> tuple[ResearchPaper, bool]:
        """Returns (record, created). Idempotent on content_id."""
        result = await self.session.execute(
            select(ResearchPaper).where(ResearchPaper.content_id == data["content_id"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing, False

        authors_raw = data.get("authors", [])
        authors_json = json.dumps(authors_raw) if isinstance(authors_raw, list) else authors_raw

        # Parse github_metrics_collected_at if it's a string
        gm_at = data.get("github_metrics_collected_at")
        if isinstance(gm_at, str):
            try:
                gm_at = datetime.fromisoformat(gm_at.replace("Z", "+00:00"))
            except ValueError:
                gm_at = None

        record = ResearchPaper(
            content_id=data["content_id"],
            title=data["title"],
            authors=authors_json,
            source_url=data["source_url"],
            github_url=data.get("github_url"),
            github_stars=data.get("github_stars"),
            github_metrics_collected_at=gm_at,
            published_at=data.get("published_at"),
            date_extraction_method=data.get("date_extraction_method", "arxiv_api"),
            date_confidence=data.get("date_confidence", 0.99),
            run_id=data.get("run_id"),
        )
        self.session.add(record)
        await self.session.commit()
        return record, True

    async def count(self) -> int:
        from sqlalchemy import func
        result = await self.session.execute(select(func.count()).select_from(ResearchPaper))
        return result.scalar_one()

    async def all_for_export(self) -> list[ResearchPaper]:
        result = await self.session.execute(select(ResearchPaper))
        return list(result.scalars().all())


class StartupRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, data: dict[str, Any]) -> tuple[Startup, bool]:
        result = await self.session.execute(
            select(Startup).where(Startup.content_id == data["content_id"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing, False
        record = Startup(
            content_id=data["content_id"],
            raw_name=data["raw_name"],
            canonical_name=data.get("canonical_name"),
            source_name=data["source_name"],
            source_url=data["source_url"],
            employee_count=data.get("employee_count"),
            description=data.get("description"),
            domain=data.get("domain"),
            resolution_status=data.get("resolution_status", "UNRESOLVED"),
            matching_method=data.get("matching_method"),
            confidence=data.get("confidence"),
            run_id=data.get("run_id"),
        )
        self.session.add(record)
        await self.session.commit()
        return record, True

    async def all_for_export(self) -> list[Startup]:
        result = await self.session.execute(select(Startup))
        return list(result.scalars().all())


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, data: dict[str, Any]) -> tuple[Product, bool]:
        result = await self.session.execute(
            select(Product).where(Product.content_id == data["content_id"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing, False
        record = Product(
            content_id=data["content_id"],
            product_name=data["product_name"],
            startup_name=data.get("startup_name"),
            pricing_model=data.get("pricing_model"),
            source_name=data["source_name"],
            source_url=data["source_url"],
            run_id=data.get("run_id"),
        )
        self.session.add(record)
        await self.session.commit()
        return record, True

    async def all_for_export(self) -> list[Product]:
        result = await self.session.execute(select(Product))
        return list(result.scalars().all())


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, data: dict[str, Any]) -> tuple[Job, bool]:
        result = await self.session.execute(
            select(Job).where(Job.content_id == data["content_id"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing, False
        record = Job(
            content_id=data["content_id"],
            title=data["title"],
            company=data.get("company"),
            role_family=data.get("role_family"),
            is_remote=data.get("is_remote", False),
            source_name=data["source_name"],
            source_url=data["source_url"],
            published_at=data.get("published_at"),
            collected_at=data.get("collected_at"),
            date_extraction_method=data.get("date_extraction_method"),
            date_confidence=data.get("date_confidence"),
            run_id=data.get("run_id"),
        )
        self.session.add(record)
        await self.session.commit()
        return record, True

    async def fresh_for_export(self, freshness_hours: int = 24) -> list[Job]:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=freshness_hours)
        result = await self.session.execute(
            select(Job).where(Job.published_at >= cutoff)
        )
        return list(result.scalars().all())


class NewsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, data: dict[str, Any]) -> tuple[News, bool]:
        result = await self.session.execute(
            select(News).where(News.content_id == data["content_id"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing, False
        record = News(
            content_id=data["content_id"],
            title=data["title"],
            source_name=data["source_name"],
            source_url=data["source_url"],
            canonical_url=data.get("canonical_url"),
            published_at=data.get("published_at"),
            collected_at=data.get("collected_at"),
            date_extraction_method=data.get("date_extraction_method"),
            date_confidence=data.get("date_confidence"),
            run_id=data.get("run_id"),
        )
        self.session.add(record)
        await self.session.commit()
        return record, True

    async def fresh_for_export(self, freshness_hours: int = 24) -> list[News]:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=freshness_hours)
        result = await self.session.execute(
            select(News).where(News.published_at >= cutoff)
        )
        return list(result.scalars().all())


class EntityMappingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_resolution(self, data: dict[str, Any]) -> EntityMapping:
        record = EntityMapping(
            raw_name=data["raw_name"],
            canonical_name=data.get("canonical_name"),
            entity_type=data["entity_type"],
            matching_method=data.get("matching_method"),
            confidence=data.get("confidence"),
            resolution_status=data.get("resolution_status", "UNRESOLVED"),
            source_url=data.get("source_url"),
            run_id=data.get("run_id"),
        )
        self.session.add(record)
        await self.session.commit()
        return record

    async def all_for_export(self) -> list[EntityMapping]:
        result = await self.session.execute(select(EntityMapping))
        return list(result.scalars().all())
