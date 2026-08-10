import streamlit as st
import os
import sys
import pandas as pd
import asyncio
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.storage.database import AsyncSessionLocal
from src.models.job import Job
from src.models.news import News
from dashboard.style import apply_premium_style

st.set_page_config(page_title="Fresh Signals", layout="wide")
apply_premium_style()

st.title("Fresh Signals")
st.markdown("<div class='subtext'>Real-time intelligence feed strictly bounded within a 24-hour publication window.</div>", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_signals():
    async def _fetch():
        async with AsyncSessionLocal() as session:
            jobs_res = await session.execute(select(Job))
            news_res = await session.execute(select(News))
            return jobs_res.scalars().all(), news_res.scalars().all()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    jobs, news = loop.run_until_complete(_fetch())
    
    jobs_data = []
    for j in jobs:
        jobs_data.append({
            "Title": j.title,
            "Company": j.company or "Unknown",
            "Published": j.published_at.strftime("%Y-%m-%d %H:%M") if j.published_at else "Unknown",
            "Remote": "Yes" if j.is_remote else "No",
            "Role Family": j.role_family,
            "Source URL": j.source_url
        })
        
    news_data = []
    for n in news:
        news_data.append({
            "Title": n.title,
            "Source": n.source_name,
            "Published": n.published_at.strftime("%Y-%m-%d %H:%M") if n.published_at else "Unknown",
            "Status": "Verified < 24h",
            "Source URL": n.source_url
        })
        
    return pd.DataFrame(jobs_data), pd.DataFrame(news_data)

try:
    df_jobs, df_news = fetch_signals()
    
    tab1, tab2 = st.tabs(["NEWS SIGNALS", "JOB SIGNALS"])
    
    with tab1:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if df_news.empty:
            st.markdown("""
            <div style="padding: 40px; text-align: center; border: 1px solid #eaeaea; border-radius: 4px; background: #fafafa;">
                <div style="font-weight: 600; margin-bottom: 8px;">No verified news signals</div>
                <div style="color: #666; font-size: 0.9rem;">The pipeline did not find any news articles published within the strict 24-hour window.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='font-size:0.8rem; font-weight:600; margin-bottom:10px; color:#666;'>{len(df_news)} FRESH ARTICLES</div>", unsafe_allow_html=True)
            st.dataframe(df_news, use_container_width=True, hide_index=True, column_config={"Source URL": st.column_config.LinkColumn("Source URL")})
            
    with tab2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if df_jobs.empty:
            st.markdown("""
            <div style="padding: 40px; text-align: center; border: 1px solid #eaeaea; border-radius: 4px; background: #fafafa;">
                <div style="font-weight: 600; margin-bottom: 8px;">No verified job signals</div>
                <div style="color: #666; font-size: 0.9rem;">The pipeline did not find any job postings published within the strict 24-hour window.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='font-size:0.8rem; font-weight:600; margin-bottom:10px; color:#666;'>{len(df_jobs)} FRESH POSTINGS</div>", unsafe_allow_html=True)
            st.dataframe(df_jobs, use_container_width=True, hide_index=True, column_config={"Source URL": st.column_config.LinkColumn("Source URL")})

except Exception as e:
    st.error(f"Failed to load Signal data: {str(e)}")
