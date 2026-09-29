import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
import pandas as pd
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.tools.controlled_tools import ControlledPolarTools

st.set_page_config(page_title="Polar Expeditions | NCPOR", page_icon="🚢", layout="wide")
render_sidebar()

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 style="color: #38BDF8; margin: 0;">🚢 Indian Scientific Expeditions to Polar Regions</h2>
    <p style="color: #94A3B8; margin: 0.3rem 0;">Historic and contemporary research voyages to Antarctica, the Arctic, and the Southern Ocean</p>
</div>
""", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([2, 1])
with col_s1:
    search_term = st.text_input("Search Expeditions by Leader, Vessel, or Keyword", "")
with col_s2:
    region_filter = st.selectbox("Region Filter", ["All", "Antarctica", "Arctic", "Southern Ocean"])

expeditions = ControlledPolarTools.search_expeditions(
    query_term=search_term if search_term else None,
    region=region_filter if region_filter != "All" else None
)

st.write(f"Showing **{len(expeditions)}** expedition records:")

for exp in expeditions:
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h3 style="color: #38BDF8; margin: 0 0 0.4rem 0;">{exp['title']}</h3>
                <div style="font-size: 0.85rem; color: #94A3B8;">
                    🗓️ <strong>Season</strong>: {exp['season_year']} | 
                    🧭 <strong>Region</strong>: {exp['region']} | 
                    👨‍✈️ <strong>Leader</strong>: {exp['leader']} | 
                    ⛴️ <strong>Vessel</strong>: {exp['vessel']}
                </div>
            </div>
            <span style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem;">
                {exp['departure']} to {exp['return']}
            </span>
        </div>
        <p style="color: #CBD5E1; margin: 0.8rem 0; font-size: 0.95rem;">
            <strong>Key Objectives & Research Mandate:</strong><br>{exp['objectives']}
        </p>
        <div style="font-size: 0.8rem;">
            <a href="{exp['report_url']}" target="_blank" style="color: #38BDF8; text-decoration: none;">📄 View Official Expedition Report (NCPOR DSpace) ↗</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
