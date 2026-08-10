# Scale Benchmark Report

> [!NOTE]
> This is a **Controlled ingestion benchmark with simulated network latency**. 
> External production throughput will be constrained by actual network latency, source rate limits, LLM latency, provider quotas, GitHub API limits, and database disk IO.

## Results

**1,000 Records (Concurrency: 50):**
- Runtime: 5.308 seconds
- Throughput: 188.40 tasks/sec
- Success Rate: 100.0%
- Failure Rate: 0.0%

**10,000 Records (Concurrency: 100):**
- Runtime: 25.991 seconds
- Throughput: 384.74 tasks/sec
- Success Rate: 100.0%
- Failure Rate: 0.0%

## Production Scaling to 500k+
This architecture scales linearly to 500,000+ records through:
1. **Queue-Based Distribution**: The `WorkerPool` isolates task ingestion from execution via `asyncio.Queue`.
2. **Horizontal Scaling**: In production, the single event loop is replaced by distributed workers (e.g., Celery/Kafka) picking off a central Redis/RabbitMQ queue.
3. **Database Indexing**: The SQLite prototype is replaced by PostgreSQL with strict unique `B-tree` indexes on `content_id`, ensuring fast idempotent `UPSERT` operations via SQLAlchemy.
4. **Connection Pooling**: PostgreSQL `pgbouncer` manages the thousands of DB connections efficiently.
5. **Caching**: Resolved entities are cached in Redis to prevent redundant RapidFuzz computations on popular companies.
