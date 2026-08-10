from __future__ import annotations
from src.config.logging import get_logger

log = get_logger("provenance")


def validate_provenance(record: dict, required_fields: list[str] | None = None) -> bool:
    """
    Gate 1: source_url must exist and start with http.
    Gate 3: required_fields must all be non-null and non-empty.

    Returns False and logs on any violation.
    """
    source_url = record.get("source_url", "")
    if not source_url or not str(source_url).startswith("http"):
        log.warning(
            "provenance_missing_source_url",
            record_id=record.get("content_id"),
        )
        return False

    if required_fields:
        for field in required_fields:
            val = record.get(field)
            if val is None or str(val).strip() == "":
                log.warning(
                    "provenance_missing_required_field",
                    field=field,
                    record_id=record.get("content_id"),
                )
                return False

    return True
