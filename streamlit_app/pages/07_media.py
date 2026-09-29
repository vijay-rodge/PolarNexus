import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
import pandas as pd
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.tools.controlled_tools import ControlledPolarTools
from scientific_engine.document_analyzer import DocumentAnalyzer

st.set_page_config(page_title="Media Gallery | NCPOR", page_icon="📸", layout="wide")
render_sidebar()

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 style="color: #38BDF8; margin: 0;">📸 Polar Expeditions & Stations Media Dissemination Gallery</h2>
    <p style="color: #94A3B8; margin: 0.3rem 0;">Curated high-resolution imagery, satellite orbital geometry diagrams, and survey map archives from Antarctica and the Arctic</p>
</div>
""", unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)
with col_f1:
    stations = ["All", "Maitri", "Bharati", "Dakshin Gangotri", "Himadri", "IndARC", "Himansh"]
    station_select = st.selectbox("Filter by Station / Location", stations)
with col_f2:
    categories = ["All", "Technical Diagram & Survey Maps", "Station Infrastructure", "Aurora", "Wildlife"]
    category_select = st.selectbox("Filter by Media Category", categories)

media_items = ControlledPolarTools.search_media(
    station_name=station_select if station_select != "All" else None,
    category=category_select if category_select != "All" else None
)

st.write(f"Showing **{len(media_items)}** authenticated polar media records:")

cols = st.columns(2)
for idx, m in enumerate(media_items):
    with cols[idx % 2]:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.08); 
                    border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;">
            <h4 style="color: #38BDF8; margin: 0 0 0.5rem 0;">{m['title']}</h4>
        </div>
        """, unsafe_allow_html=True)
        st.image(m["image_url"], use_container_width=True, caption=m["caption"])
        st.caption(f"🗓️ Date: {m.get('date', 'N/A')} | 📷 Contributor: {m.get('photographer', 'NCPOR')} | 🏷️ Category: `{m.get('category')}`")
        if m.get('source_url'):
            st.markdown(f"[🔗 High-Resolution Source Archive]({m['source_url']})")

        # If it's a survey map or geodetic diagram, provide interactive coordinate map
        if "survey" in m['title'].lower() or "geodetic" in m['title'].lower() or "orbit" in m['title'].lower() or "dakshin gangotri" in m['title'].lower():
            with st.expander("🗺️ View Extracted Geodetic Coordinates"):
                benchmarks = [
                    {"name": "Automatic Weather Station (AWS)", "lat": -70.753601, "lon": 11.637116, "elev": "150.12 m", "dms": "70°45'12.963\"S, 11°38'13.618\"E"},
                    {"name": "Dakshin Gangotri Base Camp (Hut)", "lat": -69.986853, "lon": 11.918684, "elev": "35.00 m", "dms": "69°59'12.672\"S, 11°55'07.263\"E"},
                    {"name": "Base Camp (Ice Shelf)", "lat": -69.989755, "lon": 11.940786, "elev": "44.25 m", "dms": "69°59'23.119\"S, 11°56'26.830\"E"}
                ]
                st.dataframe(pd.DataFrame(benchmarks), use_container_width=True)
                st.map(pd.DataFrame([{"lat": b["lat"], "lon": b["lon"]} for b in benchmarks]), zoom=7)
        
        st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.15;'>", unsafe_allow_html=True)
