import pytest
import asyncio
from src.crawlers.http_client import HttpClient, TokenBucketRateLimiter
from src.llm.orchestrator import LLMOrchestrator
from src.llm.base import LLMProvider
from src.llm.chunking import chunk_text, count_tokens
from src.resolution.resolver import SeedEntityIndex
from src.resolution.normaliser import normalise_name
from src.validation.provenance import validate_provenance
from src.extraction.schemas import StartupSchema, ResearchPaperSchema
from src.validation.schema_validator import validate_record
from pydantic import ValidationError
import time
import json

# ==========================================
# HTTP TESTS
# ==========================================

@pytest.mark.asyncio
async def test_token_bucket():
    bucket = TokenBucketRateLimiter(capacity=2, refill_rate=10.0)
    assert bucket.tokens == 2
    await bucket.acquire(1)
    assert bucket.tokens <= 1

@pytest.mark.asyncio
async def test_http_429_backoff_and_jitter(mocker):
    class MockResp:
        def __init__(self, status):
            self.status = status
            self.headers = {"Retry-After": "1"} if status == 429 else {}
        async def text(self, *a, **kw): return ""
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass

    class MockSession:
        def __init__(self): self.calls = 0
        def get(self, url, **kwargs):
            self.calls += 1
            return MockResp(429 if self.calls < 3 else 200)

    client = HttpClient(max_retries=3, base_backoff=0.1)
    client._session = MockSession()
    
    start = time.time()
    resp = await client.get("http://example.com/mock_429")
    elapsed = time.time() - start
    
    assert resp.status == 200
    assert client._session.calls == 3
    assert elapsed >= 0.2  # 0.1 * 1 + 0.1 * 2

@pytest.mark.asyncio
async def test_http_500_retry(mocker):
    class MockResp:
        def __init__(self, status):
            self.status = status
            self.headers = {}
        async def text(self, *a, **kw): return ""
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass

    class MockSession:
        def __init__(self): self.calls = 0
        def get(self, url, **kwargs):
            self.calls += 1
            return MockResp(500 if self.calls == 1 else 200)

    client = HttpClient(max_retries=2, base_backoff=0.1)
    client._session = MockSession()
    resp = await client.get("http://example.com/mock_500")
    assert resp.status == 200
    assert client._session.calls == 2

@pytest.mark.asyncio
async def test_http_404_fast_fail(mocker):
    class MockResp:
        def __init__(self, status):
            self.status = status
            self.headers = {}
        async def text(self, *a, **kw): return ""
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass

    class MockSession:
        def __init__(self): self.calls = 0
        def get(self, url, **kwargs):
            self.calls += 1
            return MockResp(404)

    client = HttpClient(max_retries=2)
    client._session = MockSession()
    resp = await client.get("http://example.com/mock_404")
    assert resp.status == 404
    assert client._session.calls == 1  # No retries on 404

# ==========================================
# LLM & CHUNKING TESTS
# ==========================================

def test_token_counting():
    text = "Hello world this is a test"
    assert count_tokens(text) > 5

def test_semantic_chunking_paragraphs():
    p1 = "word " * 1000
    p2 = "word " * 1000
    text = f"{p1}\n\n{p2}"
    chunks = list(chunk_text(text, max_tokens=1500))
    assert len(chunks) == 2

def test_semantic_chunking_hard_limit():
    # Force single string with no spaces
    text = "A" * 10000 
    chunks = list(chunk_text(text, max_tokens=100))
    assert len(chunks) > 10
    assert max(count_tokens(c) for c in chunks) <= 100

class MockProvider(LLMProvider):
    def __init__(self, name, fail_count=0):
        self.provider_name = name
        self.calls = 0
        self.fail_count = fail_count
    def is_available(self): return True
    async def extract(self, text, schema, prompt):
        self.calls += 1
        if self.calls <= self.fail_count:
            raise Exception("Mock 429")
        return {"result": self.provider_name}

@pytest.mark.asyncio
async def test_llm_orchestrator_fallback():
    gemini = MockProvider("gemini", fail_count=5)  # Exhausts retries
    groq = MockProvider("groq", fail_count=1)      # Succeeds on retry 2
    deepseek = MockProvider("deepseek", fail_count=0)

    orch = LLMOrchestrator()
    orch.providers = [gemini, groq, deepseek]
    
    # Must patch settings.llm_max_retries for speed
    import src.config.settings
    src.config.settings.settings.llm_max_retries = 2
    
    res = await orch.extract("test", {}, "test")
    assert res == {"result": "groq"}
    assert gemini.calls == 2
    assert groq.calls == 2
    assert deepseek.calls == 0

@pytest.mark.asyncio
async def test_llm_orchestrator_all_fail():
    gemini = MockProvider("gemini", fail_count=5)
    orch = LLMOrchestrator()
    orch.providers = [gemini]
    import src.config.settings
    src.config.settings.settings.llm_max_retries = 1
    res = await orch.extract("test", {}, "test")
    assert res == {}

# ==========================================
# ENTITY RESOLUTION TESTS
# ==========================================

def test_normaliser_lowercase():
    assert normalise_name("OpenAI") == "openai"

def test_normaliser_punctuation():
    assert normalise_name("OpenAI, Inc.") == "openai"

def test_normaliser_legal_suffixes():
    assert normalise_name("GraphOne LLC") == "graphone"
    assert normalise_name("FrontierAtlas Co Ltd") == "frontieratlas"

def test_normaliser_whitespace():
    assert normalise_name("  Meta   AI  ") == "meta ai"

def test_resolver_exact():
    r = SeedEntityIndex()
    r.normalised_map = {"openai": "OpenAI"}
    canon, method, conf = r.resolve("OpenAI, Inc.")
    assert canon == "OpenAI"
    assert method == "exact"
    assert conf == 100.0

def test_resolver_fuzzy():
    r = SeedEntityIndex()
    r.normalised_map = {"anthropic": "Anthropic"}
    canon, method, conf = r.resolve("Anthropc")
    assert canon == "Anthropic"
    assert method == "fuzzy"
    assert conf > 85.0

def test_resolver_unresolved():
    r = SeedEntityIndex()
    r.normalised_map = {"openai": "OpenAI"}
    canon, method, conf = r.resolve("RandomStartup")
    assert canon is None
    assert method == "none"
    assert conf < 85.0

# ==========================================
# PROVENANCE & SCHEMA TESTS
# ==========================================

def test_provenance_valid():
    rec = {"source_url": "https://example.com", "name": "Test"}
    assert validate_provenance(rec, ["name", "source_url"]) is True

def test_provenance_missing_field():
    rec = {"source_url": "https://example.com"}
    assert validate_provenance(rec, ["name", "source_url"]) is False

def test_provenance_invalid_url():
    rec = {"source_url": "not-a-url", "name": "Test"}
    assert validate_provenance(rec, ["name", "source_url"]) is False # our custom logic says if not startswith http

def test_schema_valid():
    from src.extraction.schemas import StartupSchema
    valid = validate_record(StartupSchema, {
        "content_id": "1",
        "raw_name": "Test",
        "source_name": "test",
        "source_url": "https://test.com"
    })
    assert valid is not None

def test_schema_invalid_url_pydantic():
    from src.extraction.schemas import StartupSchema
    valid = validate_record(StartupSchema, {
        "content_id": "1",
        "raw_name": "Test",
        "source_name": "test",
        "source_url": "ftp://test.com"
    })
    assert valid is None

def test_schema_pricing_enum():
    from src.extraction.schemas import ProductSchema
    valid = validate_record(ProductSchema, {
        "content_id": "1",
        "product_name": "Prod",
        "source_name": "test",
        "source_url": "https://test.com",
        "pricing_model": "FREE"
    })
    assert valid is not None
    assert valid.pricing_model.value == "FREE"

def test_schema_pricing_enum_invalid():
    from src.extraction.schemas import ProductSchema
    valid = validate_record(ProductSchema, {
        "content_id": "1",
        "product_name": "Prod",
        "source_name": "test",
        "source_url": "https://test.com",
        "pricing_model": "CHEAP"
    })
    assert valid is None
