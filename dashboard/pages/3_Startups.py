import streamlit as st
import os
import sys
import pandas as pd
import asyncio
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.storage.database import AsyncSessionLocal
from src.models.startup import Startup
from dashboard.style import apply_premium_style

st.set_page_config(page_title="Startup Intelligence", layout="wide")
apply_premium_style()

st.title("Startup Intelligence")
st.markdown("<div class='subtext'>Canonical directory of AI organizations and foundational metrics.</div>", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_startups():
    async def _fetch():
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Startup))
            return result.scalars().all()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    startups = loop.run_until_complete(_fetch())
    
    data = []
    for s in startups:
        data.append({
            "Startup Name": s.canonical_name or s.raw_name,
            "Employees": s.employee_count,
            "Source": s.source_name,
            "Collected": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "Unknown",
            "Source URL": s.source_url
        })
    return pd.DataFrame(data)

try:
    df = fetch_startups()
    
    if df.empty:
        st.markdown("""
        <div style="padding: 40px; text-align: center; border: 1px solid #eaeaea; border-radius: 4px; background: #fafafa; margin-top: 20px;">
            <div style="font-weight: 600; margin-bottom: 8px;">No verified signals</div>
            <div style="color: #666; font-size: 0.9rem;">The pipeline did not find records matching this filter.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("Search startups...", label_visibility="collapsed", placeholder="Search organization name...")
        with col2:
            sources = df["Source"].unique().tolist()
            selected_source = st.selectbox("Filter by Source", ["All Sources"] + sources, label_visibility="collapsed")
        
        filtered_df = df.copy()
        if search:
            filtered_df = filtered_df[filtered_df["Startup Name"].str.contains(search, case=False, na=False)]
        if selected_source != "All Sources":
            filtered_df = filtered_df[filtered_df["Source"] == selected_source]
            
        st.markdown(f"<div style='font-size:0.8rem; font-weight:600; margin-bottom:10px; color:#666;'>SHOWING {len(filtered_df)} RECORDS</div>", unsafe_allow_html=True)
        
        display_df = filtered_df.copy()
        display_df["Employees"] = display_df["Employees"].fillna("Unknown")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source URL": st.column_config.LinkColumn("Source URL")
            }
        )

except Exception as e:
    st.error(f"Failed to load Startup data: {str(e)}")
