from __future__ import annotations
import os
import json
from gspread.exceptions import SpreadsheetNotFound
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.storage.repositories import (
    ResearchPaperRepository, StartupRepository, ProductRepository,
    JobRepository, NewsRepository, EntityMappingRepository
)
from src.config.logging import get_logger

log = get_logger("google_sheets_exporter")


class GoogleSheetsExporter:
    def __init__(self, spreadsheet_name: str = "GraphOne Intelligence Pipeline"):
        self.spreadsheet_name = spreadsheet_name
        self.scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        self.client = self._authenticate()
        self.spreadsheet = None

    def _authenticate(self):
        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not creds_json:
            log.warning("google_sheets_auth_missing", msg="No GOOGLE_SERVICE_ACCOUNT_JSON env var found.")
            return None
        
        try:
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scopes)
            return gspread.authorize(creds)
        except Exception as exc:
            log.error("google_sheets_auth_failed", error=str(exc))
            return None

    def _get_or_create_spreadsheet(self):
        if not self.client:
            return None
        try:
            return self.client.open(self.spreadsheet_name)
        except SpreadsheetNotFound:
            log.info("creating_new_spreadsheet", name=self.spreadsheet_name)
            return self.client.create(self.spreadsheet_name)

    def _get_or_create_worksheet(self, title: str, rows: int = 1000, cols: int = 20):
        if not self.spreadsheet:
            return None
        try:
            return self.spreadsheet.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            log.info("creating_new_worksheet", title=title)
            return self.spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)

    def _write_data(self, worksheet_name: str, headers: list[str], data: list[list]):
        if not self.client:
            return
        if not self.spreadsheet:
            self.spreadsheet = self._get_or_create_spreadsheet()
        
        if not self.spreadsheet:
            return

        ws = self._get_or_create_worksheet(worksheet_name)
        if not ws:
            return

        # Prepare payload
        payload = [headers] + data
        
        # Clear existing and update
        try:
            ws.clear()
            ws.update(payload, 'A1') # update range A1
            log.info("google_sheets_update_success", worksheet=worksheet_name, rows=len(data))
        except Exception as exc:
            log.error("google_sheets_update_failed", worksheet=worksheet_name, error=str(exc))

    async def export_all(self, session: AsyncSession) -> None:
        if not self.client:
            log.warning("skipping_google_sheets_export", reason="Not authenticated")
            return

        log.info("starting_google_sheets_export")

        # 1. Startups
        startups = await StartupRepository(session).all_for_export()
        if startups:
            headers = [
                "content_id", "raw_name", "canonical_name", "source_name",
                "source_url", "employee_count", "domain", "resolution_status",
                "matching_method", "confidence"
            ]
            data = [[
                s.content_id, s.raw_name, s.canonical_name, s.source_name,
                s.source_url, s.employee_count, s.domain, s.resolution_status,
                s.matching_method, s.confidence
            ] for s in startups]
            self._write_data("Startups", headers, data)

        # 2. Products
        products = await ProductRepository(session).all_for_export()
        if products:
            headers = [
                "content_id", "product_name", "startup_name", "pricing_model",
                "source_name", "source_url"
            ]
            data = [[
                p.content_id, p.product_name, p.startup_name, p.pricing_model,
                p.source_name, p.source_url
            ] for p in products]
            self._write_data("Products", headers, data)

        # 3. Research Papers
        papers = await ResearchPaperRepository(session).all_for_export()
        if papers:
            headers = [
                "content_id", "title", "authors", "source_url", "canonical_url",
                "github_url", "github_stars", "github_metrics_collected_at",
                "published_at", "date_extraction_method", "date_confidence"
            ]
            data = [[
                p.content_id, p.title, p.authors, p.source_url, p.canonical_url,
                p.github_url, p.github_stars, p.github_metrics_collected_at,
                str(p.published_at) if p.published_at else "", 
                p.date_extraction_method, p.date_confidence
            ] for p in papers]
            self._write_data("Research Papers", headers, data)

        # 4. Jobs
        jobs = await JobRepository(session).fresh_for_export(24)
        if jobs:
            headers = [
                "content_id", "title", "company", "role_family", "is_remote",
                "source_name", "source_url", "published_at"
            ]
            data = [[
                j.content_id, j.title, j.company, j.role_family, j.is_remote,
                j.source_name, j.source_url, str(j.published_at) if j.published_at else ""
            ] for j in jobs]
            self._write_data("Jobs", headers, data)

        # 5. News
        news = await NewsRepository(session).fresh_for_export(24)
        if news:
            headers = [
                "content_id", "title", "source_name", "source_url", "published_at"
            ]
            data = [[
                n.content_id, n.title, n.source_name, n.source_url, str(n.published_at) if n.published_at else ""
            ] for n in news]
            self._write_data("News", headers, data)

        # 6. Entity Mapping Log
        mappings = await EntityMappingRepository(session).all_for_export()
        if mappings:
            headers = [
                "raw_name", "canonical_name", "entity_type", "matching_method",
                "confidence", "resolution_status", "source_url"
            ]
            data = [[
                m.raw_name, m.canonical_name, m.entity_type, m.matching_method,
                m.confidence, m.resolution_status, m.source_url
            ] for m in mappings]
            self._write_data("Entity Mapping Log", headers, data)
            
        log.info("google_sheets_export_complete")
