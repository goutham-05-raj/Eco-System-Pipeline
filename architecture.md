# GraphOne Intelligence Pipeline — Architecture

## 1. System Architecture & Data Flow
The pipeline follows a highly concurrent, asynchronous, modular architecture.

**Sources → Crawlers → LLM Chunking/Extraction → Entity Resolution → Validation → Database → Export**

1. **Sources**: arXiv, GitHub, YCombinator, F6S, Futurepedia, AI Jobs, RSS Feeds.
2. **Crawlers**: Asynchronous Python classes leveraging `aiohttp` and `BeautifulSoup4`. Requests are funneled through a central `HttpClient` that manages rate limits via a Token Bucket algorithm and handles exponential backoff.
3. **Extraction & LLM Orchestration**:
   - Deterministic extraction is prioritized (e.g. 7-tier date parsing checking `JSON-LD`, `<meta>`, regex, etc).
   - Unstructured data is processed by `tiktoken`-based semantic chunking.
   - The `LLMOrchestrator` attempts Gemini Flash, falling back to Groq Llama, and finally DeepSeek, ensuring high availability.
4. **Entity Resolution**: Normalized names run through a `RapidFuzz` index against a ground-truth configuration (`seed_entities.json`), assigning a confidence score to resolve variants (e.g., "OpenAI Inc" -> "OpenAI").
5. **Validation & Storage**: Pydantic models enforce strict schema requirements (e.g., non-null valid `source_url`). Failed records are logged and dropped. Valid records are UPSERTED idempotently into an Async SQLAlchemy SQLite backend.

---

## 2. Reliability Mechanisms

### 429 Handling
`HttpClient` intercepts HTTP 429 errors. It parses the `Retry-After` header. If absent, it applies an exponential backoff (`base_backoff * 2^(attempt-1) + jitter`) to prevent thundering herd problems against Cloudflare or Datadome boundaries.

### 413 Handling & Chunking
Rather than blindly truncating the first N characters (which destroys context), `chunk_text()` splits large text semantically—falling from paragraphs, to newlines, to spaces, down to raw token limits—ensuring every chunk passed to the LLM respects the strict context window limit.

### LLM Fallback & Anti-Hallucination
The pipeline expects LLMs to fail (timeouts, 500s) or hallucinate. The fallback orchestrator gracefully switches providers. If the LLM returns fabricated URLs or hallucinates GitHub stars, the deterministic Pydantic Validation layer rejects the payload entirely.

### Idempotency & Deduplication
Every row in the database utilizes a `content_id` primary key, generated via a SHA-256 hash of the *canonical, normalized URL*. This guarantees that duplicate crawler runs, pagination overlaps, or multiple workers scraping the same link result in a fast `UPSERT` update rather than duplicate records.

---

## 3. Scale Strategy: 500k+ Production Deployment

While the local architecture uses `asyncio.Queue` and SQLite, it is designed identically to production paradigms. To scale to 500,000+ records, the following component swaps occur:

1. **Queueing (Kafka / RabbitMQ)**
   Instead of in-memory `asyncio.Queue`, jobs (URLs to scrape) are pushed to a distributed message broker.
2. **Workers (Celery / Temporal)**
   The `WorkerPool` logic scales horizontally across Kubernetes pods. Each worker acts autonomously, pulling from the broker.
3. **Database (PostgreSQL + PgBouncer)**
   SQLite is replaced by PostgreSQL. The deterministic `content_id` becomes a unique B-Tree index. `PgBouncer` is deployed to multiplex thousands of async SQLAlchemy connections into a small pool of actual Postgres connections.
4. **Caching (Redis)**
   As the dataset scales, fuzzy-matching entity resolution becomes CPU intensive. Redis caches `(raw_name -> canonical_name)` tuples so that frequent flyers (e.g., OpenAI) resolve in O(1) time.
5. **Failure Isolation**
   Crawler workers, extraction workers, and LLM workers are separated into different pod deployments to isolate failures and allow independent auto-scaling.
