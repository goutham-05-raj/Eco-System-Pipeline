from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.crawlers.arxiv import ArxivCrawler
from src.crawlers.papers_with_code import PapersWithCodeCrawler
from src.crawlers.github import GitHubClient
from src.crawlers.startups import StartupCrawler
from src.crawlers.products import ProductCrawler
from src.crawlers.jobs import JobsCrawler
from src.crawlers.news import NewsCrawler
from src.storage.repositories import (
    ResearchPaperRepository, StartupRepository, ProductRepository,
    JobRepository, NewsRepository, EntityMappingRepository
)
from src.resolution.resolver import SeedEntityIndex
from src.validation.schema_validator import validate_record
from src.validation.provenance import validate_provenance
from src.validation.freshness import is_fresh
from src.extraction.schemas import (
    ResearchPaperSchema, StartupSchema, ProductSchema, JobSchema, NewsSchema
)
from src.llm.orchestrator import LLMOrchestrator
from src.config.logging import get_logger

log = get_logger("runner")


class PipelineRunner:
    """
    Coordinates the entire end-to-end intelligence pipeline.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.run_id = f"run_{uuid.uuid4().hex[:8]}"
        self.llm = LLMOrchestrator()
        log.info("pipeline_initialized", run_id=self.run_id)

    async def run_research_pipeline(self, max_items: int = 1000) -> None:
        log.info("starting_research_pipeline")
        arxiv = ArxivCrawler()
        pwc = PapersWithCodeCrawler()
        gh = GitHubClient()
        repo = ResearchPaperRepository(self.session)

        # 1. Fetch arXiv
        papers = await arxiv.crawl(max_results=max_items)
        log.info("arxiv_fetch_complete", count=len(papers))

        # 2. Enrich with GitHub URLs via PWC
        papers = await pwc.enrich(papers)
        log.info("pwc_enrichment_complete")

        # 3. Enrich with GitHub Stars
        for paper in papers:
            if paper.get("github_url"):
                gh_data = await gh.get_stars(paper["github_url"])
                paper["github_stars"] = gh_data.get("github_stars")
                paper["github_metrics_collected_at"] = gh_data.get("github_metrics_collected_at")
            paper["run_id"] = self.run_id

            # 4. Validate and Save
            if not validate_provenance(paper, ["title", "source_url"]):
                continue

            valid = validate_record(ResearchPaperSchema, paper)
            if valid:
                # pass dict representation for repo upsert
                await repo.upsert(valid.model_dump())

    async def run_startups_pipeline(self) -> None:
        log.info("starting_startups_pipeline")
        crawler = StartupCrawler()
        resolver = SeedEntityIndex()
        repo = StartupRepository(self.session)
        map_repo = EntityMappingRepository(self.session)

        startups = await crawler.crawl_all()
        for s in startups:
            s["run_id"] = self.run_id
            if not validate_provenance(s, ["raw_name", "source_url"]):
                continue

            # Entity resolution
            canonical, method, conf = resolver.resolve(s["raw_name"])
            if canonical:
                s["canonical_name"] = canonical
                s["matching_method"] = method
                s["confidence"] = conf
                s["resolution_status"] = "RESOLVED"
            else:
                s["resolution_status"] = "UNRESOLVED"

            await map_repo.log_resolution({
                "raw_name": s["raw_name"],
                "canonical_name": s.get("canonical_name"),
                "entity_type": "STARTUP",
                "matching_method": s.get("matching_method"),
                "confidence": s.get("confidence"),
                "resolution_status": s["resolution_status"],
                "source_url": s["source_url"],
                "run_id": self.run_id,
            })

            valid = validate_record(StartupSchema, s)
            if valid:
                await repo.upsert(valid.model_dump())

    async def run_products_pipeline(self) -> None:
        log.info("starting_products_pipeline")
        crawler = ProductCrawler()
        repo = ProductRepository(self.session)

        from src.extraction.heuristics import extract_pricing_heuristic
        import asyncio

        products = await crawler.crawl_all()
        llm_calls_made = 0
        MAX_LLM_ENRICHMENTS = 10  # Cap LLM calls per run to respect Gemini Free Tier 15 RPM limit

        for p in products:
            p["run_id"] = self.run_id
            if not validate_provenance(p, ["product_name", "source_url"]):
                continue

            # 1. Apply fast heuristic extraction
            if p.get("pricing_model") is None:
                heuristic_model = extract_pricing_heuristic(p["product_name"])
                if heuristic_model:
                    p["pricing_model"] = heuristic_model

            # 2. LLM Enrichment for remaining missing fields (throttled)
            if (p.get("startup_name") is None or p.get("pricing_model") is None) and llm_calls_made < MAX_LLM_ENRICHMENTS:
                schema_hint = {
                    "startup_name": "string (the company that made the product, or None)",
                    "pricing_model": "string (one of: FREE, FREEMIUM, PAID, ENTERPRISE) or None"
                }
                prompt = (
                    "Extract the company/startup name and the pricing model from the product details. "
                    "If the company name is not mentioned, return null/None. "
                    "If the pricing model is not clear, return null/None."
                )
                text_context = f"Product Name/Title: {p['product_name']}"
                
                try:
                    llm_calls_made += 1
                    extracted = await self.llm.extract(text=text_context, schema_hint=schema_hint, prompt=prompt)
                    if extracted:
                        if p.get("startup_name") is None and extracted.get("startup_name"):
                            p["startup_name"] = extracted["startup_name"]
                        if p.get("pricing_model") is None and extracted.get("pricing_model"):
                            model = str(extracted["pricing_model"]).upper()
                            if model in ["FREE", "FREEMIUM", "PAID", "ENTERPRISE"]:
                                p["pricing_model"] = model
                except Exception as exc:
                    log.warning("llm_product_enrichment_failed", error=str(exc), product=p["product_name"])
                
                # Throttle to stay within Free Tier Rate Limit (15 RPM = 4s per request)
                await asyncio.sleep(1.0)

            valid = validate_record(ProductSchema, p)
            if valid:
                await repo.upsert(valid.model_dump(exclude_none=False))

    async def run_news_pipeline(self) -> None:
        log.info("starting_news_pipeline")
        crawler = NewsCrawler()
        repo = NewsRepository(self.session)

        news = await crawler.crawl_all()
        for n in news:
            n["run_id"] = self.run_id
            if not validate_provenance(n, ["title", "source_url"]):
                continue

            # In RSS, we get raw string dates, we normally run them through extraction.dates
            # For simplicity in this demo wrapper, assume RSS gives clean dates or we use
            # extraction fallback
            from src.extraction.dates import extract_date
            dt_info = extract_date("", {}, n.get("raw_published", ""))
            
            # Intelligent Heuristic: If missing date, check if we've seen it before
            if not dt_info["published_at"]:
                from sqlalchemy import select
                from src.models.news import News
                existing = await self.session.execute(select(News).where(News.content_id == n["content_id"]))
                existing = existing.scalar_one_or_none()
                
                if existing and existing.collected_at:
                    dt_info["published_at"] = existing.collected_at
                    dt_info["method"] = "heuristic_inherited"
                    dt_info["confidence"] = 0.5
                else:
                    from datetime import datetime, timezone
                    dt_info["published_at"] = datetime.now(timezone.utc)
                    dt_info["method"] = "heuristic_new"
                    dt_info["confidence"] = 0.1

            n["published_at"] = dt_info["published_at"]
            n["date_extraction_method"] = dt_info["method"]
            n["date_confidence"] = dt_info["confidence"]

            if not is_fresh(n["published_at"], 24):
                continue  # Skip stale news

            valid = validate_record(NewsSchema, n)
            if valid:
                await repo.upsert(valid.model_dump())

    async def run_jobs_pipeline(self) -> None:
        log.info("starting_jobs_pipeline")
        crawler = JobsCrawler()
        repo = JobRepository(self.session)

        jobs = await crawler.crawl_all()
        for j in jobs:
            j["run_id"] = self.run_id
            if not validate_provenance(j, ["title", "source_url"]):
                continue

            from src.extraction.dates import extract_date
            from datetime import datetime, timezone
            dt_info = extract_date("", {}, j.get("published_raw", ""))
            # Intelligent Heuristic: If missing date, check if we've seen it before
            if not dt_info["published_at"]:
                from sqlalchemy import select
                from src.models.job import Job
                existing = await self.session.execute(select(Job).where(Job.content_id == j["content_id"]))
                existing = existing.scalar_one_or_none()
                
                if existing and existing.collected_at:
                    dt_info["published_at"] = existing.collected_at
                    dt_info["method"] = "heuristic_inherited"
                    dt_info["confidence"] = 0.5
                else:
                    dt_info["published_at"] = datetime.now(timezone.utc)
                    dt_info["method"] = "heuristic_new"
                    dt_info["confidence"] = 0.1

            j["published_at"] = dt_info["published_at"]
            j["date_extraction_method"] = dt_info["method"]
            j["date_confidence"] = dt_info["confidence"]
            j["collected_at"] = datetime.now(timezone.utc)

            # Job listings are relevant for 7 days (unlike news which is 24 hours)
            if not is_fresh(j["published_at"], 168):
                continue

            valid = validate_record(JobSchema, j)
            if valid:
                await repo.upsert(valid.model_dump())
