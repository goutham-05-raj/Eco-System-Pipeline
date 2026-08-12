import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import sys

async def check():
    engine = create_async_engine("sqlite+aiosqlite:///j:/unstop/graphone-intelligence-pipeline/graphone.db")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        startups = await session.execute(text("SELECT count(*) FROM startups"))
        products = await session.execute(text("SELECT count(*) FROM products"))
        jobs = await session.execute(text("SELECT count(*) FROM jobs"))
        news = await session.execute(text("SELECT count(*) FROM news"))
        papers = await session.execute(text("SELECT count(*) FROM research_papers"))
        
        print(f"Startups: {startups.scalar()}")
        print(f"Products: {products.scalar()}")
        print(f"Jobs: {jobs.scalar()}")
        print(f"News: {news.scalar()}")
        print(f"Papers: {papers.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
