import streamlit as st
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.style import apply_premium_style

st.set_page_config(
    page_title="GraphOne Intelligence Engine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_premium_style()




# Top Bar mock (Search)
col_logo, col_search, col_status = st.columns([1, 2, 1])
with col_logo:
    st.markdown("<div style='padding-top:10px; font-weight:900; font-size:1rem; color:#000000; letter-spacing:0.05em;'>GRAPHONE <span style='font-weight:800; font-size:0.8rem; color:#000000; margin-left:8px;'>INTELLIGENCE ENGINE</span></div>", unsafe_allow_html=True)
with col_search:
    st.text_input("Search (⌘ K)", placeholder="Search intelligence...", label_visibility="collapsed")
with col_status:
    st.markdown("<div style='text-align: right; font-size: 0.9rem; font-weight:800; padding-top: 10px; color:#000000;'>● Pipeline Operational</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("<div style='font-weight:700; font-size:1.1rem; color:#1e293b; margin-bottom: 20px;'>GraphOne Engine</div>", unsafe_allow_html=True)

run_id = st.sidebar.text_input("Pipeline Run ID", value="run_final_e8742588", disabled=True)
st.sidebar.caption("Last Updated: Just now")
st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Check DB status
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "graphone.db")
db_status = "Operational" if os.path.exists(db_path) else "Error"
badge_class = "badge-success" if db_status == "Operational" else "badge-error"
st.sidebar.markdown(f"<span class='badge {badge_class}'>DB: {db_status}</span>", unsafe_allow_html=True)

# Check Google Sheets status
gs_configured = bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
gs_status = "Configured" if gs_configured else "Unconfigured"
badge_class_gs = "badge-primary" if gs_configured else "badge-warning"
st.sidebar.markdown(f"<span class='badge {badge_class_gs}' style='margin-top:8px;'>GS: {gs_status}</span>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    
st.sidebar.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
st.sidebar.caption("GraphOne Premium Platform v1.0")

# Hero Section — sky blue banner only here
st.markdown("""
<div style="
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    border-radius: 20px;
    padding: 40px 48px;
    margin-top: 10px;
    margin-bottom: 30px;
    border: 1px solid rgba(0,0,0,0.07);
    box-shadow: 0 4px 20px rgba(14,165,233,0.12);
">
    <div style="font-size: 2.4rem; font-weight: 900; color: #000000; letter-spacing: -0.02em; line-height: 1.2; margin-bottom: 14px;">
        AI ECOSYSTEM INTELLIGENCE
    </div>
    <div style="font-size: 1.1rem; color: #000000; font-weight: 800; line-height: 1.6; margin-bottom: 6px;">
        Discover, enrich and resolve the world's rapidly changing AI ecosystem.
    </div>
    <div style="font-size: 1.05rem; color: #0c4a6e; font-weight: 600; line-height: 1.6;">
        Continuously ingest and monitor intelligence across startups, products, research, jobs and news.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; max-width: 600px; margin: 0 auto; margin-top: 50px; background: rgba(255,255,255,0.55); border: 1px solid rgba(0,0,0,0.10); border-radius: 16px; padding: 32px; backdrop-filter: blur(10px);">
    <h3 style="margin-top:0; color:#000000; font-weight:900; font-size:1.4rem;">Welcome to GraphOne</h3>
    <p style="color:#000000; font-weight:700; font-size:1rem;">Please use the sidebar to navigate the intelligence modules.</p>
</div>
""", unsafe_allow_html=True)
