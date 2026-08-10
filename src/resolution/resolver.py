from __future__ import annotations
import json
from rapidfuzz import fuzz, process
from pathlib import Path
from src.resolution.normaliser import normalise_name
from src.config.logging import get_logger

log = get_logger("resolver")


class SeedEntityIndex:
    """
    In-memory index of canonical entity names (the "seed" list).
    """
    def __init__(self, seed_file: str | Path = "data/seed_entities.json") -> None:
        self.canonical_names: list[str] = []
        self.normalised_map: dict[str, str] = {}
        self._load(seed_file)

    def _load(self, seed_file: str | Path) -> None:
        path = Path(seed_file)
        if not path.exists():
            log.warning("seed_file_missing", path=str(path))
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Support both array of strings and dict {"entities": [...]}
            if isinstance(data, dict) and "entities" in data:
                self.canonical_names = data["entities"]
            elif isinstance(data, list):
                self.canonical_names = data

            for name in self.canonical_names:
                norm = normalise_name(name)
                if norm:
                    self.normalised_map[norm] = name
            log.info("seed_index_loaded", count=len(self.canonical_names))
        except Exception as exc:
            log.error("seed_load_error", error=str(exc))

    def resolve(self, raw_name: str, threshold: float = 85.0) -> tuple[str | None, str, float]:
        """
        Attempt to resolve raw_name against the seed list.
        Returns: (canonical_name, method, confidence)
        method is "exact", "fuzzy", or "none".
        """
        if not raw_name or not self.normalised_map:
            return None, "none", 0.0

        norm_raw = normalise_name(raw_name)

        # 1. Exact match on normalised form
        if norm_raw in self.normalised_map:
            return self.normalised_map[norm_raw], "exact", 100.0

        # 2. Fuzzy match
        # ExtractOne returns (match_string, score, index)
        match = process.extractOne(
            norm_raw,
            self.normalised_map.keys(),
            scorer=fuzz.WRatio
        )

        if match:
            best_match, score, _ = match
            if score >= threshold:
                canonical = self.normalised_map[best_match]
                return canonical, "fuzzy", score

        return None, "none", 0.0
