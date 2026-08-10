# GraphOne Intelligence Engine

## 1. Overview
A production-ready data engineering and intelligence pipeline that asynchronously scrapes, cleans, extracts, and resolves entity data across startups, AI products, research papers, tech jobs, and AI news. Built for the GraphOne / FrontierAtlas AI Engineer assessment.

## 2. Architecture
The system consists of an async Python crawler backend, a SQLAlchemy SQLite database, a fallback LLM orchestrator, a Google Sheets exporter, and a Streamlit observability dashboard. (See `architecture.pdf` for the detailed flow).

## 3. Features
- Async Queue-Based Ingestion
- Multi-LLM Fallback (Gemini -> Groq -> DeepSeek)
- Exact/Fuzzy Entity Resolution
- Streamlit Demo Dashboard
- Google Sheets Service Account Sync

## 4. Data Sources
- **Startups**: YCombinator API, F6S.
- **Products**: HackerNews Algolia API, Futurepedia, There's An AI For That.
- **Papers**: arXiv API, PapersWithCode, GitHub API.
- **Jobs**: AIJobs, HackerNews, RemoteOK.
- **News**: RSS Feeds (TechCrunch, VentureBeat, KDnuggets, AI News, Google AI).

## 5. Data Integrity
Every record enforces provenance strictly via Pydantic. If an LLM hallucinates a URL, the row is rejected entirely. Duplicate processing is safely handled via `content_id` hashes enabling idempotent Upserts.

## 6. LLM Orchestration
The pipeline gracefully recovers from LLM rate limits by cascading sequentially through Gemini (Primary), Groq (Fast Fallback), and DeepSeek (Final Fallback).

## 7. 429 Handling
HTTP 429s trigger an exponential backoff sequence respecting `Retry-After` headers, wrapped around a TokenBucket rate limiter.

## 8. 413 Handling
Semantic chunking via `tiktoken` bounds large HTML payloads to strict context window limits.

## 9. Entity Resolution
Uses `RapidFuzz` to normalize names (e.g., "OpenAI Inc." -> "OpenAI") with strict confidence thresholds.

## 10. Freshness
Enforces strict 24-hour UTC boundaries on News and Jobs using a 7-tier date parser.

## 11. Database
Async SQLAlchemy over SQLite (`graphone.db`) for local testing.

## 12. Google Sheets
Dynamically provisions and updates 6 tabs inside Google Sheets without duplicating rows.

## 13. Dashboard
A read-only professional Streamlit application that surfaces database metrics and intelligence.

## 14. Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install fpdf2 streamlit pandas
```

## 15. Environment Setup
Create a `.env` file from `.env.example`:
```
GOOGLE_SERVICE_ACCOUNT_JSON=...
GOOGLE_SHEET_ID=...
```

## 16. Running Pipeline
```bash
python run.py
```

## 17. Running Dashboard
```bash
streamlit run dashboard/app.py
```

## 18. Running Tests
```bash
pytest -q
```

## 19. Benchmark
Controlled ingestion benchmark simulating network latency:
```bash
python scripts/run_benchmark.py
```

## 20. Known Limitations
- Single IP scraping is subject to Cloudflare blocks.
- Synchronous semantic chunking can block the event loop under heavy load.
- Google Sheets is bound to a 60-request-per-minute write quota.

## 21. Production Scaling
Horizontal scaling via Celery pods reading off Kafka/RabbitMQ into a PostgreSQL cluster with PgBouncer connection pooling.
