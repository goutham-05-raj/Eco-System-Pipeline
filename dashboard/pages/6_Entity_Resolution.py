import streamlit as st
import os
import sys
import pandas as pd
import asyncio
from sqlalchemy import select, func

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.storage.database import AsyncSessionLocal
from src.models.entity_mapping import EntityMapping
from dashboard.style import apply_premium_style

st.set_page_config(page_title="Entity Resolution", layout="wide")
apply_premium_style()

st.title("Entity Resolution")
st.markdown("<div class='subtext'>Canonicalizing fragmented names across heterogeneous intelligence sources.</div>", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_mappings():
    async def _fetch():
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(EntityMapping))
            return result.scalars().all()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    mappings = loop.run_until_complete(_fetch())
    
    data = []
    for m in mappings:
        data.append({
            "Raw Entity": m.raw_name,
            "Normalized Entity": m.raw_name.lower() if m.raw_name else "",
            "Canonical Entity": m.canonical_name or "UNRESOLVED",
            "Method": m.matching_method or "NONE",
            "Confidence": f"{round(m.confidence, 1)}%" if m.confidence else "0%"
        })
    return pd.DataFrame(data)

try:
    df = fetch_mappings()
    
    if df.empty:
        st.info("No entity mapping records found.")
    else:
        # Visual resolution flow
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; background-color: #fafafa; border: 1px solid #eaeaea; padding: 20px; border-radius: 4px; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; margin-bottom: 30px;">
            <div style="text-align: center; width: 20%;"><div style="font-weight: 600; margin-bottom: 5px;">RAW INPUT</div><div>"Open AI, Inc."</div></div>
            <div style="color: #ccc;">→</div>
            <div style="text-align: center; width: 20%;"><div style="font-weight: 600; margin-bottom: 5px;">NORMALIZE</div><div>"open ai inc"</div></div>
            <div style="color: #ccc;">→</div>
            <div style="text-align: center; width: 20%;"><div style="font-weight: 600; margin-bottom: 5px;">FUZZY MATCH</div><div>RapidFuzz Score: 94</div></div>
            <div style="color: #ccc;">→</div>
            <div style="text-align: center; width: 20%;"><div style="font-weight: 600; margin-bottom: 5px;">CANONICAL ENTITY</div><div style="color: #000;">"OpenAI"</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        exact = df[df["Method"] == "EXACT"].shape[0]
        fuzzy = df[df["Method"] == "FUZZY"].shape[0]
        unresolved = df[df["Canonical Entity"] == "UNRESOLVED"].shape[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Entities", len(df))
        with col2: st.metric("Exact Matches", exact)
        with col3: st.metric("Fuzzy Matches", fuzzy)
        with col4: st.metric("Unresolved", unresolved)
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search = st.text_input("Search", label_visibility="collapsed", placeholder="Search raw or canonical name...")
        with col_filter:
            methods = df["Method"].unique().tolist()
            selected_method = st.selectbox("Match Method", ["All Methods"] + methods, label_visibility="collapsed")
            
        filtered_df = df.copy()
        if search:
            filtered_df = filtered_df[
                filtered_df["Raw Entity"].str.contains(search, case=False, na=False) |
                filtered_df["Canonical Entity"].str.contains(search, case=False, na=False)
            ]
        if selected_method != "All Methods":
            filtered_df = filtered_df[filtered_df["Method"] == selected_method]
            
        st.markdown(f"<div style='font-size:0.8rem; font-weight:600; margin-bottom:10px; color:#666;'>SHOWING {len(filtered_df)} MAPPINGS</div>", unsafe_allow_html=True)
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Failed to load Entity Mapping data: {str(e)}")
