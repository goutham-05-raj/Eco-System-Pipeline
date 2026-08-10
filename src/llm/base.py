from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    provider_name: str = "unknown"

    @abstractmethod
    async def extract(
        self,
        text: str,
        schema_hint: dict[str, Any],
        prompt: str,
    ) -> dict[str, Any]:
        """
        Extract structured data from text.
        Must return a dict.
        Must NOT invent values not present in 'text'.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the API key is configured."""
        ...
