from __future__ import annotations
import json
import asyncio
from typing import Any
from src.llm.base import LLMProvider
from src.config.settings import settings
from src.config.logging import get_logger

log = get_logger("gemini")


class GeminiProvider(LLMProvider):
    provider_name = "gemini"
    MODEL = "gemini-1.5-flash"

    def __init__(self) -> None:
        self._model = None
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self._model = genai.GenerativeModel(self.MODEL)
            except ImportError:
                log.warning("gemini_sdk_not_installed")

    def is_available(self) -> bool:
        return bool(settings.gemini_api_key) and self._model is not None

    async def extract(
        self, text: str, schema_hint: dict[str, Any], prompt: str
    ) -> dict[str, Any]:
        if not self._model:
            raise RuntimeError("Gemini not configured")
        full_prompt = f"{prompt}\n\nReturn ONLY valid JSON. No markdown fences.\n\nText:\n{text}"
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: self._model.generate_content(full_prompt)
        )
        raw = response.text.strip()
        # Strip markdown code fences if model adds them despite instructions
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
