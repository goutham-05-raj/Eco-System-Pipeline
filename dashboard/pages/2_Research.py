import streamlit as st
import os
import sys
import pandas as pd
import asyncio
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.storage.database import AsyncSessionLocal
from src.models.research_paper import ResearchPaper
from dashboard.style import apply_premium_style

st.set_page_config(page_title="Research Intelligence", layout="wide")
apply_premium_style()

st.title("Research Intelligence")
st.markdown("<div class='subtext'>AI research papers enriched with publication metadata and repository signals.</div>", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_papers():
    async def _fetch():
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(ResearchPaper).limit(1000))
            return result.scalars().all()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    papers = loop.run_until_complete(_fetch())
    
    data = []
    for p in papers:
        data.append({
            "Title": p.title,
            "Authors": p.authors,
            "Published Date": p.published_at.strftime("%Y-%m-%d") if p.published_at else "Unknown",
            "GitHub Availability": "Yes" if p.github_url else "No",
            "Stars": p.github_stars if p.github_stars is not None else 0,
            "Source URL": p.source_url
        })
    return pd.DataFrame(data)

try:
    df = fetch_papers()
    
    if df.empty:
        st.markdown("""
        <div style="padding: 40px; text-align: center; border: 1px solid #eaeaea; border-radius: 4px; background: #fafafa; margin-top: 20px;">
            <div style="font-weight: 600; margin-bottom: 8px;">No verified signals</div>
            <div style="color: #666; font-size: 0.9rem;">The pipeline did not find records matching this filter.<br>Try adjusting the date range or source filter.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Minimal Filters
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("Search papers...", label_visibility="collapsed", placeholder="Search by title or author...")
        with col2:
            min_stars = st.number_input("Minimum Stars", min_value=0, value=0, label_visibility="collapsed")
        with col3:
            gh_only = st.selectbox("GitHub Availability", ["All Papers", "Has GitHub Repo"], label_visibility="collapsed")
            
        filtered_df = df.copy()
        
        if search:
            filtered_df = filtered_df[
                filtered_df["Title"].str.contains(search, case=False, na=False) |
                filtered_df["Authors"].str.contains(search, case=False, na=False)
            ]
        if min_stars > 0:
            filtered_df = filtered_df[pd.to_numeric(filtered_df["Stars"]) >= min_stars]
        if gh_only == "Has GitHub Repo":
            filtered_df = filtered_df[filtered_df["GitHub Availability"] == "Yes"]
            
        st.markdown(f"<div style='font-size:0.8rem; font-weight:600; margin-bottom:10px; color:#666;'>SHOWING {len(filtered_df)} RECORDS</div>", unsafe_allow_html=True)
        
        # Display data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source URL": st.column_config.LinkColumn("Source URL")
            }
        )

except Exception as e:
    st.error(f"Failed to load Research data: {str(e)}")
