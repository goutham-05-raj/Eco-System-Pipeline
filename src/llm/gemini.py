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

    def __init__(self) -> None:
        self._genai = None
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self._genai = genai
            except ImportError:
                log.warning("gemini_sdk_not_installed")

    def is_available(self) -> bool:
        return bool(settings.gemini_api_key) and self._genai is not None

    async def extract(
        self, text: str, schema_hint: dict[str, Any], prompt: str
    ) -> dict[str, Any]:
        if not self._genai:
            raise RuntimeError("Gemini not configured")
        full_prompt = f"{prompt}\n\nReturn ONLY valid JSON. No markdown fences.\n\nText:\n{text}"
        
        candidate_models = []
        if settings.gemini_model:
            candidate_models.append(settings.gemini_model)

        # Discover active models dynamically from Google API for this API key
        try:
            loop = asyncio.get_event_loop()
            live_models = await loop.run_in_executor(
                None,
                lambda: [
                    m.name for m in self._genai.list_models()
                    if "generateContent" in getattr(m, "supported_generation_methods", [])
                ]
            )
            candidate_models.extend(live_models)
        except Exception as list_exc:
            log.warning("gemini_list_models_failed", error=str(list_exc))

        # Fallback candidates if dynamic listing fails
        candidate_models.extend([
            "models/gemini-1.5-flash-8b",
            "models/gemini-1.5-pro",
            "models/gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "gemini-2.0-flash",
        ])

        # Remove duplicates while preserving insertion order
        candidate_models = list(dict.fromkeys(candidate_models))

        loop = asyncio.get_event_loop()
        last_exc = None

        for model_name in candidate_models:
            try:
                model_inst = self._genai.GenerativeModel(model_name)
                response = await loop.run_in_executor(
                    None, lambda: model_inst.generate_content(full_prompt)
                )
                raw = response.text.strip()
                if raw.startswith("```"):
                    parts = raw.split("```")
                    raw = parts[1] if len(parts) > 1 else raw
                    if raw.startswith("json"):
                        raw = raw[4:]
                return json.loads(raw.strip())
            except Exception as exc:
                last_exc = exc
                log.warning("gemini_model_attempt_failed", model=model_name, error=str(exc))
                continue

        if last_exc:
            raise last_exc
        raise RuntimeError("Gemini extraction failed for all candidate models")
