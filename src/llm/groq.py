from __future__ import annotations
import json
from typing import Any
from src.llm.base import LLMProvider
from src.config.settings import settings
from src.config.logging import get_logger

log = get_logger("groq")


class GroqProvider(LLMProvider):
    provider_name = "groq"

    def __init__(self) -> None:
        self._clients: list[Any] = []
        self._key_index = 0
        if settings.groq_api_key:
            keys = [k.strip() for k in settings.groq_api_key.split(",") if k.strip()]
            try:
                from groq import AsyncGroq
                for key in keys:
                    self._clients.append(AsyncGroq(api_key=key))
            except ImportError:
                log.warning("groq_sdk_not_installed")

    def is_available(self) -> bool:
        return len(self._clients) > 0

    async def extract(
        self, text: str, schema_hint: dict[str, Any], prompt: str
    ) -> dict[str, Any]:
        if not self._clients:
            raise RuntimeError("Groq not configured")
        full_prompt = f"{prompt}\n\nReturn ONLY valid JSON.\n\nText:\n{text}"

        candidate_models = [
            settings.groq_model,
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ]
        candidate_models = list(dict.fromkeys(candidate_models))

        last_exc = None
        # Try across each registered API key client
        for idx in range(len(self._clients)):
            client = self._clients[(self._key_index + idx) % len(self._clients)]
            for model_name in candidate_models:
                try:
                    response = await client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": full_prompt}],
                        temperature=0.0,
                        response_format={"type": "json_object"},
                    )
                    # Advance key index for round-robin balancing
                    self._key_index = (self._key_index + idx + 1) % len(self._clients)
                    return json.loads(response.choices[0].message.content)
                except Exception as exc:
                    last_exc = exc
                    log.warning(
                        "groq_attempt_failed",
                        key_index=idx,
                        model=model_name,
                        error=str(exc),
                    )
                    continue

        if last_exc:
            raise last_exc
        raise RuntimeError("Groq extraction failed for all API keys and candidate models")
