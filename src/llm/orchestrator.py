from __future__ import annotations
from typing import Any
from src.llm.base import LLMProvider
from src.llm.gemini import GeminiProvider
from src.llm.groq import GroqProvider
from src.llm.deepseek import DeepSeekProvider
from src.llm.retry import with_llm_retry
from src.config.settings import settings
from src.config.logging import get_logger

log = get_logger("llm_orchestrator")


class LLMOrchestrator:
    """
    Manages provider fallback (Gemini → Groq → DeepSeek) and retry logic.
    """

    def __init__(self) -> None:
        self.providers: list[LLMProvider] = []
        available: dict[str, LLMProvider] = {
            "gemini": GeminiProvider(),
            "groq": GroqProvider(),
            "deepseek": DeepSeekProvider(),
        }

        order = [p.strip().lower() for p in settings.llm_provider_order.split(",")]
        for p_name in order:
            provider = available.get(p_name)
            if provider and provider.is_available():
                self.providers.append(provider)

        if not self.providers:
            log.warning("no_llm_providers_configured")

    async def extract(
        self, text: str, schema_hint: dict[str, Any], prompt: str
    ) -> dict[str, Any]:
        """
        Attempt extraction across configured providers in order.
        Each provider gets up to llm_max_retries.
        Falls back to the next provider on terminal failure (e.g. 429 exhaustion or 413).
        """
        if not self.providers:
            return {}

        # Intelligent Chunking: Prevent 413 Payload Too Large
        # Retain the first 7500 and last 7500 chars (most semantically dense parts)
        MAX_CHARS = 15000
        if len(text) > MAX_CHARS:
            log.warning("llm_payload_truncated", original_len=len(text))
            text = text[:7500] + "\n\n...[TRUNCATED]...\n\n" + text[-7500:]

        last_error = None
        for provider in self.providers:
            try:
                async def _call() -> dict[str, Any]:
                    return await provider.extract(text, schema_hint, prompt)

                result = await with_llm_retry(
                    _call,
                    max_retries=settings.llm_max_retries,
                    base_backoff=1.0,
                )
                log.info(
                    "llm_extraction_success",
                    provider=provider.provider_name,
                )
                return result
            except Exception as exc:
                last_error = exc
                log.warning(
                    "llm_provider_failed",
                    provider=provider.provider_name,
                    error=str(exc),
                )
                # Fall through to next provider

        log.error("llm_all_providers_failed", final_error=str(last_error))
        return {}
