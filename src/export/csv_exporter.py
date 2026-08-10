from __future__ import annotations
import csv
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.storage.repositories import (
    ResearchPaperRepository, StartupRepository, ProductRepository,
    JobRepository, NewsRepository, EntityMappingRepository
)
from src.config.logging import get_logger

log = get_logger("csv_export")


async def export_to_csv(session: AsyncSession, output_dir: str = "data/export") -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Papers
    papers = await ResearchPaperRepository(session).all_for_export()
    if papers:
        with open(out / "research_papers.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "content_id", "title", "authors", "source_url", "canonical_url",
                "github_url", "github_stars", "github_metrics_collected_at",
                "published_at", "date_extraction_method", "date_confidence"
            ])
            for p in papers:
                writer.writerow([
                    p.content_id, p.title, p.authors, p.source_url, p.canonical_url,
                    p.github_url, p.github_stars, p.github_metrics_collected_at,
                    p.published_at, p.date_extraction_method, p.date_confidence
                ])
        log.info("csv_export_done", table="research_papers", count=len(papers))

    # Startups
    startups = await StartupRepository(session).all_for_export()
    if startups:
        with open(out / "startups.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "content_id", "raw_name", "canonical_name", "source_name",
                "source_url", "employee_count", "domain", "resolution_status",
                "matching_method", "confidence"
            ])
            for s in startups:
                writer.writerow([
                    s.content_id, s.raw_name, s.canonical_name, s.source_name,
                    s.source_url, s.employee_count, s.domain, s.resolution_status,
                    s.matching_method, s.confidence
                ])
        log.info("csv_export_done", table="startups", count=len(startups))

    # Products
    products = await ProductRepository(session).all_for_export()
    if products:
        with open(out / "products.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "content_id", "product_name", "startup_name", "pricing_model",
                "source_name", "source_url"
            ])
            for p in products:
                writer.writerow([
                    p.content_id, p.product_name, p.startup_name, p.pricing_model,
                    p.source_name, p.source_url
                ])
        log.info("csv_export_done", table="products", count=len(products))

    # Jobs (Fresh)
    jobs = await JobRepository(session).fresh_for_export(24)
    if jobs:
        with open(out / "jobs_24h.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "content_id", "title", "company", "role_family", "is_remote",
                "source_name", "source_url", "published_at"
            ])
            for j in jobs:
                writer.writerow([
                    j.content_id, j.title, j.company, j.role_family, j.is_remote,
                    j.source_name, j.source_url, j.published_at
                ])
        log.info("csv_export_done", table="jobs", count=len(jobs))

    # News (Fresh)
    news = await NewsRepository(session).fresh_for_export(24)
    if news:
        with open(out / "news_24h.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "content_id", "title", "source_name", "source_url", "published_at"
            ])
            for n in news:
                writer.writerow([
                    n.content_id, n.title, n.source_name, n.source_url, n.published_at
                ])
        log.info("csv_export_done", table="news", count=len(news))

    # Entity Mappings (Audit)
    mappings = await EntityMappingRepository(session).all_for_export()
    if mappings:
        with open(out / "entity_mappings_audit.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "raw_name", "canonical_name", "entity_type", "matching_method",
                "confidence", "resolution_status", "source_url"
            ])
            for m in mappings:
                writer.writerow([
                    m.raw_name, m.canonical_name, m.entity_type, m.matching_method,
                    m.confidence, m.resolution_status, m.source_url
                ])
        log.info("csv_export_done", table="entity_mappings", count=len(mappings))
