# Architecture

1. **Extraction Tier**: `arxiv.py`, `startups.py`, `jobs.py`. Uses `http_client.py` with exponential backoff + jitter and domain-aware rate limiting.
2. **Validation Tier**: Deterministic parsers (`dates.py`, `metadata.py`, `html_cleaner.py`). Anti-hallucination prompt headers. Pydantic schemas enforce type invariants.
3. **Resolution Tier**: `resolver.py` maps raw names to canonical seed entities using string normalisation + RapidFuzz WRatio.
4. **Storage Tier**: PostgreSQL via SQLAlchemy async session. Uses deterministic SHA256 of canonical URLs as idempotency keys.
5. **Orchestration**: `pipeline/runner.py` drives the flow.

(Export this document as a PDF to fulfil the `architecture.pdf` requirement.)
