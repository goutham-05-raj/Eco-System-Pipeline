import streamlit as st
import os
import sys
import pandas as pd
import asyncio
import altair as alt
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.storage.database import AsyncSessionLocal
from src.models.product import Product
from dashboard.style import apply_premium_style

st.set_page_config(page_title="Product Intelligence", layout="wide")
apply_premium_style()

st.title("Product Intelligence")
st.markdown("<div class='subtext'>Discovered AI products, tools, and pricing models.</div>", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_products():
    async def _fetch():
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Product))
            return result.scalars().all()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    products = loop.run_until_complete(_fetch())
    
    data = []
    for p in products:
        data.append({
            "Product": p.product_name,
            "Company": p.startup_name or "Unknown",
            "Pricing": p.pricing_model or "UNKNOWN",
            "Source": p.source_name,
            "Collected": p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "Unknown",
            "Source URL": p.source_url
        })
    return pd.DataFrame(data)

try:
    df = fetch_products()
    
    if df.empty:
        st.markdown("""
        <div style="padding: 40px; text-align: center; border: 1px solid #eaeaea; border-radius: 4px; background: #fafafa; margin-top: 20px;">
            <div style="font-weight: 600; margin-bottom: 8px;">No verified signals</div>
            <div style="color: #666; font-size: 0.9rem;">The pipeline did not find product records.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("Search products...", label_visibility="collapsed", placeholder="Search product or company...")
        with col2:
            sources = df["Source"].unique().tolist()
            selected_source = st.selectbox("Source", ["All Sources"] + sources, label_visibility="collapsed")
        with col3:
            pricing_models = df["Pricing"].unique().tolist()
            selected_pricing = st.selectbox("Pricing Model", ["All Pricing"] + pricing_models, label_visibility="collapsed")
        
        filtered_df = df.copy()
        if search:
            filtered_df = filtered_df[
                filtered_df["Product"].str.contains(search, case=False, na=False) |
                filtered_df["Company"].str.contains(search, case=False, na=False)
            ]
        if selected_source != "All Sources":
            filtered_df = filtered_df[filtered_df["Source"] == selected_source]
        if selected_pricing != "All Pricing":
            filtered_df = filtered_df[filtered_df["Pricing"] == selected_pricing]
            
        col_chart, col_data = st.columns([1, 3])
        
        with col_chart:
            st.markdown("<div style='font-size:0.8rem; font-weight:600; margin-bottom:10px; color:#666;'>DISTRIBUTION</div>", unsafe_allow_html=True)
            dist = filtered_df["Pricing"].value_counts().reset_index()
            dist.columns = ["Pricing", "Count"]
            
            # Use Altair to force black/gray styling instead of default Streamlit colors
            chart = alt.Chart(dist).mark_bar(color='#333333', cornerRadiusEnd=2).encode(
                x=alt.X('Count:Q', axis=None),
                y=alt.Y('Pricing:N', sort='-x', axis=alt.Axis(labelColor='#000', titleColor='#000', tickColor='#000', domainColor='#eaeaea')),
                tooltip=['Pricing', 'Count']
            ).properties(height=200).configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
            
        with col_data:
            st.markdown(f"<div style='font-size:0.8rem; font-weight:600; margin-bottom:10px; color:#666;'>SHOWING {len(filtered_df)} RECORDS</div>", unsafe_allow_html=True)
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Source URL": st.column_config.LinkColumn("Source URL")
                }
            )

except Exception as e:
    st.error(f"Failed to load Product data: {str(e)}")
