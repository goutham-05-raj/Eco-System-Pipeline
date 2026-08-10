from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///graphone.db"
    )

    # LLM Providers
    gemini_api_key: str = Field(default="")
    groq_api_key: str = Field(default="")
    deepseek_api_key: str = Field(default="")

    # GitHub
    github_token: str = Field(default="")

    # Google Sheets
    google_service_account: str = Field(default="")

    # Optional Redis
    redis_url: str = Field(default="")

    # Pipeline tuning
    max_concurrency: int = Field(default=10)
    llm_max_retries: int = Field(default=4)
    freshness_hours: int = Field(default=24)
    log_level: str = Field(default="INFO")

    # LLM provider order — comma-separated
    llm_provider_order: str = Field(default="gemini,groq,deepseek")

    # Spreadsheet export
    google_spreadsheet_id: str = Field(default="")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
