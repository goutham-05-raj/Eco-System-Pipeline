import streamlit as st
import os
import sys
import asyncio
from sqlalchemy import select, func

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.storage.database import AsyncSessionLocal
from src.models.startup import Startup
from src.models.product import Product
from src.models.research_paper import ResearchPaper
from src.models.job import Job
from src.models.news import News
from dashboard.style import apply_premium_style

st.set_page_config(page_title="Overview", layout="wide")
apply_premium_style()

st.title("Overview")
st.markdown("<div class='subtext'>High-level metrics and continuous intelligence ingestion status.</div>", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_kpis():
    async def _get():
        async with AsyncSessionLocal() as session:
            s_count = await session.execute(select(func.count()).select_from(Startup))
            p_count = await session.execute(select(func.count()).select_from(Product))
            r_count = await session.execute(select(func.count()).select_from(ResearchPaper))
            j_count = await session.execute(select(func.count()).select_from(Job))
            n_count = await session.execute(select(func.count()).select_from(News))
            
            return {
                "STARTUPS": s_count.scalar(),
                "PRODUCTS": p_count.scalar(),
                "RESEARCH PAPERS": r_count.scalar(),
                "JOBS": j_count.scalar(),
                "NEWS": n_count.scalar(),
            }
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(_get())

try:
    kpis = get_kpis()
    total = sum(kpis.values())
    
    # We will inject some custom metric colors via markdown
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="premium-card" style="border-top: 4px solid #3b82f6;">
            <div style="font-size:0.75rem; font-weight:700; color:#64748B; letter-spacing:0.05em; margin-bottom:8px;">STARTUPS</div>
            <div style="font-size:2.5rem; font-weight:800; color:#172033; letter-spacing:-0.03em;">{kpis['STARTUPS']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="premium-card" style="border-top: 4px solid #8b5cf6;">
            <div style="font-size:0.75rem; font-weight:700; color:#64748B; letter-spacing:0.05em; margin-bottom:8px;">PRODUCTS</div>
            <div style="font-size:2.5rem; font-weight:800; color:#172033; letter-spacing:-0.03em;">{kpis['PRODUCTS']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="premium-card" style="border-top: 4px solid #0ea5e9;">
            <div style="font-size:0.75rem; font-weight:700; color:#64748B; letter-spacing:0.05em; margin-bottom:8px;">RESEARCH PAPERS</div>
            <div style="font-size:2.5rem; font-weight:800; color:#172033; letter-spacing:-0.03em;">{kpis['RESEARCH PAPERS']:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(f"""
        <div class="premium-card" style="border-top: 4px solid #f59e0b;">
            <div style="font-size:0.75rem; font-weight:700; color:#64748B; letter-spacing:0.05em; margin-bottom:8px;">JOBS</div>
            <div style="font-size:2.5rem; font-weight:800; color:#172033; letter-spacing:-0.03em;">{kpis['JOBS']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="premium-card" style="border-top: 4px solid #e11d48;">
            <div style="font-size:0.75rem; font-weight:700; color:#64748B; letter-spacing:0.05em; margin-bottom:8px;">NEWS</div>
            <div style="font-size:2.5rem; font-weight:800; color:#172033; letter-spacing:-0.03em;">{kpis['NEWS']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="premium-card" style="border-top: 4px solid #4f46e5;">
            <div style="font-size:0.75rem; font-weight:700; color:#64748B; letter-spacing:0.05em; margin-bottom:8px;">TOTAL RECORDS</div>
            <div style="font-size:2.5rem; font-weight:800; color:#172033; letter-spacing:-0.03em;">{total:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
except Exception as e:
    st.error(f"Database connection failed: {str(e)}")

st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
col_a, col_b = st.columns([1, 1.5])

with col_a:
    st.subheader("Source Health")
    st.markdown("""
    <div class="premium-card">
    <table style="width:100%; text-align:left; border-collapse: collapse; font-size:0.95rem;">
      <tr style="border-bottom: 1px solid rgba(0,0,0,0.05); color: #64748B;">
        <th style="padding: 12px 0;">SOURCE</th>
        <th>STATUS</th>
        <th style="text-align:right;">RECORDS</th>
      </tr>
      <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
        <td style="padding: 16px 0; font-weight:500;">arXiv</td>
        <td><span class='badge badge-success'>Operational</span></td>
        <td style="text-align:right;" class="mono">1000</td>
      </tr>
      <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
        <td style="padding: 16px 0; font-weight:500;">Hacker News</td>
        <td><span class='badge badge-success'>Operational</span></td>
        <td style="text-align:right;" class="mono">992</td>
      </tr>
      <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
        <td style="padding: 16px 0; font-weight:500;">YCombinator</td>
        <td><span class='badge badge-success'>Operational</span></td>
        <td style="text-align:right;" class="mono">750</td>
      </tr>
      <tr>
        <td style="padding: 16px 0; font-weight:500;">RSS Feeds</td>
        <td><span class='badge badge-success'>Operational</span></td>
        <td style="text-align:right;" class="mono">4</td>
      </tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.subheader("Live Pipeline Visualization")
    st.markdown("""
    <div style="display:flex; flex-wrap:wrap; justify-content:center; align-items:center; gap:10px; margin-top:20px;">
        <div class="diagram-node" style="border-top:3px solid #64748B;">DATA SOURCES</div>
        <div class="diagram-arrow">↓</div>
        <div class="diagram-node" style="border-top:3px solid #3b82f6;">ASYNC CRAWL</div>
        <div class="diagram-arrow">↓</div>
        <div class="diagram-node" style="border-top:3px solid #0ea5e9;">VALIDATION</div>
        <div class="diagram-arrow">↓</div>
        <div class="diagram-node" style="border-top:3px solid #8b5cf6;">LLM ENRICHMENT</div>
        <div class="diagram-arrow">↓</div>
        <div class="diagram-node" style="border-top:3px solid #f43f5e;">ENTITY RESOLUTION</div>
        <div class="diagram-arrow">↓</div>
        <div class="diagram-node" style="border-top:3px solid #f59e0b;">DATABASE</div>
    </div>
    """, unsafe_allow_html=True)
