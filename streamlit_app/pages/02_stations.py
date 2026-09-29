import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
import pandas as pd
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.tools.controlled_tools import ControlledPolarTools
from streamlit_app.components.cards import render_station_card

st.set_page_config(page_title="Polar Stations | NCPOR", page_icon="🏛️", layout="wide")
render_sidebar()

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 style="color: #38BDF8; margin: 0;">🏛️ India's Polar Research Stations & Observatories</h2>
    <p style="color: #94A3B8; margin: 0.3rem 0;">Strategic bases across Antarctica, the Arctic, and the Himalayan Third Pole</p>
</div>
""", unsafe_allow_html=True)

stations = ControlledPolarTools.search_stations()
regions = ["All", "Antarctica", "Arctic", "Himalayas"]
selected_region = st.selectbox("Filter by Geographical Region", regions)

filtered_stations = stations
if selected_region != "All":
    filtered_stations = [s for s in stations if s["region"] == selected_region]

st_names = [s["name"] for s in filtered_stations]
selected_st_name = st.selectbox("Select Station for In-Depth Dossier", st_names)
selected_station = next((s for s in filtered_stations if s["name"] == selected_st_name), None)

if selected_station:
    col1, col2 = st.columns([2, 1])
    with col1:
        render_station_card(selected_station)
        st.subheader("🔬 Scientific Laboratories & Infrastructure")
        facilities = selected_station.get("facilities", [])
        if facilities:
            for f in facilities:
                st.markdown(f"- 🛰️ **{f}**")
        else:
            st.info("No specific facility list available.")
        st.subheader("📜 Historical & Operational Significance")
        st.write(selected_station.get("overview"))
    with col2:
        st.subheader("🗺️ Geographical Position")
        coords_df = pd.DataFrame([{
            "lat": selected_station["latitude"],
            "lon": selected_station["longitude"]
        }])
        st.map(coords_df, zoom=2)
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.8); padding: 1rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-top: 1rem;">
            <div style="font-size: 0.85rem; color: #94A3B8;">GEODETIC METRICS</div>
            <div style="color: #F8FAFC; margin-top: 0.5rem;">
                <strong>Latitude</strong>: {selected_station['latitude']}°<br>
                <strong>Longitude</strong>: {selected_station['longitude']}°<br>
                <strong>Commissioned</strong>: {selected_station['commissioned_year']}<br>
                <strong>Status</strong>: <span style="color: #34D399;">{selected_station['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
