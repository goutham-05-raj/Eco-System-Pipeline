from __future__ import annotations
import json
from typing import Any
from src.llm.base import LLMProvider
from src.config.settings import settings
from src.config.logging import get_logger

log = get_logger("deepseek")


class DeepSeekProvider(LLMProvider):
    provider_name = "deepseek"
    MODEL = "deepseek-chat"

    def __init__(self) -> None:
        self._client = None
        if settings.deepseek_api_key:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com",
                )
            except ImportError:
                log.warning("openai_sdk_not_installed")

    def is_available(self) -> bool:
        return bool(settings.deepseek_api_key) and self._client is not None

    async def extract(
        self, text: str, schema_hint: dict[str, Any], prompt: str
    ) -> dict[str, Any]:
        if not self._client:
            raise RuntimeError("DeepSeek not configured")
        full_prompt = f"{prompt}\n\nReturn ONLY valid JSON.\n\nText:\n{text}"
        response = await self._client.chat.completions.create(
            model=self.MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
