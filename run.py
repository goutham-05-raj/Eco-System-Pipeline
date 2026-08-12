from __future__ import annotations
import asyncio
from typing import Any
from src.config.logging import get_logger
from src.storage.database import init_db, AsyncSessionLocal
from src.pipeline.runner import PipelineRunner
from src.export.csv_exporter import export_to_csv

log = get_logger("main")


async def main() -> None:
    log.info("initializing_database")
    await init_db()

    async with AsyncSessionLocal() as session:
        runner = PipelineRunner(session)

        # 1. Startups
        await runner.run_startups_pipeline()
        
        # 2. Products
        await runner.run_products_pipeline()
        
        # 3. Research Papers
        await runner.run_research_pipeline(max_items=50)
        
        # 4. Jobs
        await runner.run_jobs_pipeline()
        
        # 5. News
        await runner.run_news_pipeline()
        
        # 6. Export to CSV & Google Sheets
        log.info("exporting_to_csv_and_google_sheets")
        from src.export.csv_exporter import export_to_csv
        from src.export.sheets import GoogleSheetsExporter
        
        await export_to_csv(session)
        
        sheets_exporter = GoogleSheetsExporter()
        await sheets_exporter.export_all(session)

        log.info("pipeline_runs_completed")

    log.info("shutdown_complete")


if __name__ == "__main__":
    asyncio.run(main())
