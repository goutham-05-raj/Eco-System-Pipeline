import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

DB = "sqlite+aiosqlite:///graphone.db"

async def check():
    engine = create_async_engine(DB)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        print("=== STARTUPS (latest 5 by updated_at) ===")
        r = await session.execute(text(
            "SELECT raw_name, created_at, updated_at FROM startups ORDER BY updated_at DESC LIMIT 5"
        ))
        for row in r.fetchall():
            print(f"  {row[0][:30]:<30}  created={row[1]}  updated={row[2]}")

        print("\n=== NEWS (latest 5) ===")
        r = await session.execute(text(
            "SELECT title, published_at, collected_at FROM news ORDER BY published_at DESC LIMIT 5"
        ))
        for row in r.fetchall():
            print(f"  {str(row[0])[:40]:<40}  published={row[1]}  collected={row[2]}")

        print("\n=== JOBS (latest 5) ===")
        r = await session.execute(text(
            "SELECT title, published_at, collected_at FROM jobs ORDER BY published_at DESC LIMIT 5"
        ))
        for row in r.fetchall():
            print(f"  {str(row[0])[:40]:<40}  published={row[1]}  collected={row[2]}")

        print("\n=== RESEARCH PAPERS (latest 5) ===")
        r = await session.execute(text(
            "SELECT title, published_at, updated_at FROM research_papers ORDER BY updated_at DESC LIMIT 5"
        ))
        for row in r.fetchall():
            print(f"  {str(row[0])[:40]:<40}  published={row[1]}  updated={row[2]}")

asyncio.run(check())
