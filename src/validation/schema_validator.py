from __future__ import annotations
from typing import Type, TypeVar
from pydantic import ValidationError
from src.extraction.schemas import SchemaBase
from src.config.logging import get_logger

log = get_logger("schema_validator")
T = TypeVar("T", bound=SchemaBase)


def validate_record(schema_class: Type[T], data: dict) -> T | None:
    """
    Validate a raw dict against the given Pydantic schema.
    Returns the validated instance or None (and logs the failure).
    """
    try:
        return schema_class(**data)
    except ValidationError as exc:
        log.warning(
            "schema_validation_failed",
            schema=schema_class.__name__,
            errors=exc.errors()[:3],
            content_id=data.get("content_id"),
        )
        return None
