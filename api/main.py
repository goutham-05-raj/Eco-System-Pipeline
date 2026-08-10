import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.storage.database import get_session
from src.models.startup import Startup
from src.models.product import Product
from src.models.research_paper import ResearchPaper
from src.models.job import Job
from src.models.news import News
from src.models.entity_mapping import EntityMapping

app = FastAPI(title="GraphOne Intelligence API")

# Allow React app to fetch data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/overview")
async def get_overview(session: AsyncSession = Depends(get_session)):
    s_count = await session.execute(select(func.count()).select_from(Startup))
    p_count = await session.execute(select(func.count()).select_from(Product))
    r_count = await session.execute(select(func.count()).select_from(ResearchPaper))
    j_count = await session.execute(select(func.count()).select_from(Job))
    n_count = await session.execute(select(func.count()).select_from(News))
    
    return {
        "startups": s_count.scalar(),
        "products": p_count.scalar(),
        "research": r_count.scalar(),
        "jobs": j_count.scalar(),
        "news": n_count.scalar(),
    }

@app.get("/api/startups")
async def get_startups(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Startup))
    startups = result.scalars().all()
    return startups

@app.get("/api/products")
async def get_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product))
    return result.scalars().all()

@app.get("/api/research")
async def get_research(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ResearchPaper))
    return result.scalars().all()

@app.get("/api/jobs")
async def get_jobs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Job))
    return result.scalars().all()

@app.get("/api/news")
async def get_news(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(News))
    return result.scalars().all()

@app.get("/api/resolution")
async def get_resolution(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(EntityMapping))
    return result.scalars().all()
