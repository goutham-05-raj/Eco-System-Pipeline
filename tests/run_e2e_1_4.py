import asyncio
import time
import json
import uuid
import sqlalchemy
from collections import defaultdict
from sqlalchemy import select, func
from src.storage.database import engine, AsyncSessionLocal, init_db
from src.storage.repositories import ResearchPaperRepository, StartupRepository, ProductRepository, JobRepository, NewsRepository, EntityMappingRepository
from src.pipeline.runner import PipelineRunner
from src.crawlers.http_client import HttpClient, HttpResponse
from src.config.logging import get_logger
from src.crawlers.papers_with_code import PWC_API

log = get_logger("e2e_tests")

async def test_1_and_4(session):
    log.info("--- TEST 1: REAL RESEARCH PAPER INGESTION ---")
    runner = PipelineRunner(session)
    repo = ResearchPaperRepository(session)
    
    # Check baseline
    initial_count = await repo.count()
    
    # Run 5
    await runner.run_research_pipeline(max_items=5)
    c5 = await repo.count()
    log.info(f"Ingested 5 papers. Total in DB: {c5}")

    # Run 25
    await runner.run_research_pipeline(max_items=25)
    c25 = await repo.count()
    log.info(f"Ingested 25 papers. Total in DB: {c25}")

    # Run 100
    await runner.run_research_pipeline(max_items=100)
    c100 = await repo.count()
    log.info(f"Ingested 100 papers. Total in DB: {c100}")
    
    log.info("--- TEST 4: DUPLICATE INGESTION ---")
    # Run the exact same 100 again
    await runner.run_research_pipeline(max_items=100)
    c_dup = await repo.count()
    log.info(f"Ran exact same 100 papers again. Total in DB: {c_dup}. Duplicates inserted: {c_dup - c100}")

async def test_2(session):
    log.info("--- TEST 2: GITHUB ENRICHMENT ---")
    repo = ResearchPaperRepository(session)
    papers = await repo.all_for_export()
    
    with_github = 0
    without_github = 0
    success = 0
    failure = 0
    
    for p in papers:
        if p.github_url:
            with_github += 1
            if p.github_stars is not None and p.github_metrics_collected_at is not None:
                success += 1
            else:
                failure += 1
        else:
            without_github += 1
            assert p.github_stars is None
            
    log.info(f"papers_with_github: {with_github}")
    log.info(f"papers_without_github: {without_github}")
    log.info(f"github_enrichment_success: {success}")
    log.info(f"github_enrichment_failure: {failure}")

async def test_3():
    log.info("--- TEST 3: PAPERSWITHCODE FAILURE RECOVERY ---")
    async with HttpClient() as client:
        # Arxiv ID that we know exists
        url = f"{PWC_API}?arxiv_id=1706.03762"
        resp = await client.get(url, rps=0.5)
        
        log.info(f"HTTP status: {resp.status}")
        log.info(f"Content-Type: {resp.headers.get('Content-Type')}")
        log.info(f"response length: {len(resp.text)}")
        log.info(f"first safe portion of response: {resp.text[:100].strip()}")
        log.info(f"request URL: {url}")
        
        is_html = "<html" in resp.text.lower()
        log.info(f"Is HTML (Cloudflare block)? {is_html}")

async def main():
    await init_db()
    async with AsyncSessionLocal() as session:
        await test_1_and_4(session)
        await test_2(session)
    await test_3()

if __name__ == "__main__":
    asyncio.run(main())
