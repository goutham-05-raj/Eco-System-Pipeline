import pytest
from pydantic import ValidationError
from src.extraction.schemas import StartupSchema, ProductSchema
from src.validation.schema_validator import validate_record

def test_startup_schema_valid():
    data = {
        "content_id": "123",
        "raw_name": "OpenAI",
        "source_name": "test",
        "source_url": "https://example.com"
    }
    obj = validate_record(StartupSchema, data)
    assert obj is not None
    assert obj.raw_name == "OpenAI"

def test_startup_schema_invalid_url():
    data = {
        "content_id": "123",
        "raw_name": "OpenAI",
        "source_name": "test",
        "source_url": "ftp://example.com"  # Must be http
    }
    obj = validate_record(StartupSchema, data)
    assert obj is None

def test_product_schema_pricing_enum():
    data = {
        "content_id": "123",
        "product_name": "GPT-4",
        "source_name": "test",
        "source_url": "https://example.com",
        "pricing_model": "INVALID"
    }
    obj = validate_record(ProductSchema, data)
    assert obj is None
