import streamlit as st
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config.settings import settings
from streamlit_app.components.cards import render_metric_card
from streamlit_app.components.sidebar import render_sidebar
from database.connection import SessionLocal
from database.models import Station, Expedition, Dataset, MediaRecord, Publication

st.set_page_config(
    page_title="PolarNexus | NCPOR Polar Science Portal",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)
render_sidebar()

st.markdown("""
<style>
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }
    .main-header {
        background: linear-gradient(90deg, #0284C7 0%, #0369A1 50%, #075985 100%);
        padding: 2.2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.3);
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.025em;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #E0F2FE;
        margin-top: 0.5rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0284C7, #0369A1);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <span style="font-size: 3rem;">❄️</span>
        <div>
            <h1 class="main-title">Polar Science Knowledge & Outreach Platform</h1>
            <p class="sub-title">National Centre for Polar and Ocean Research (NCPOR) & National Polar Data Center (NPDC) — SIH PS 26063</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

db = SessionLocal()
try:
    stations_count = db.query(Station).count()
    expeditions_count = db.query(Expedition).count()
    datasets_count = db.query(Dataset).count()
    publications_count = db.query(Publication).count()
    media_count = db.query(MediaRecord).count()
finally:
    db.close()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_metric_card("Active Stations", f"{stations_count}", "Antarctica & Arctic", "🏛️")
with col2:
    render_metric_card("Expeditions", f"{expeditions_count}", "Historic to Present", "🚢")
with col3:
    render_metric_card("NPDC Datasets", f"{datasets_count}", "Hourly AWS Archives", "📊")
with col4:
    render_metric_card("DSpace Papers", f"{publications_count}", "Peer-Reviewed", "📄")
with col5:
    render_metric_card("Media Records", f"{media_count}", "High-Res Gallery", "📸")

st.markdown("---")

col_left, col_right = st.columns([3, 2])
with col_left:
    st.subheader("💡 Intelligent Query Routing Architecture")
    st.markdown("""
    This platform implements an **industry-grade multi-pipeline RAG & ML engine** powered by **LangGraph**:
    
    * **Numerical Inquiries** (*e.g., "What was the average temperature at Maitri in 2012?"*):
      Automatically routed to the **Sandboxed Pandas Analytical Engine** to compute verified statistics from raw quality-controlled AWS sensors. **Never guessed by LLMs.**
    * **Text & Report Inquiries** (*e.g., "What research was conducted during the 15th Arctic Expedition?"*):
      Routed to **ChromaDB Vector Retrieval** with section-aware chunks and strict citation verification.
    * **Dataset Discovery** (*e.g., "What datasets are available for Maitri?"*):
      Discovers official NPDC datasets with direct access links.
    * **Educational Outreach** (*e.g., "Explain India's Antarctic research to a school student"*):
      Engaging, pedagogically-adapted synthesis with zero hallucination.
    * **Media Search** (*e.g., "Show me photographs of Bharati station"*):
      Retrieves authenticated NCPOR gallery photos with metadata.
    """)
    st.info("👈 **Select '01 AI Assistant' from the sidebar to start asking questions!**")

with col_right:
    st.subheader("🌐 Active Polar Stations Status")
    stations_info = [
        {"name": "Maitri (Antarctica)", "coords": "70°45' S, 11°44' E", "status": "🟢 Operational (Year-Round)", "temp": "-10.5 °C (Annual Mean)"},
        {"name": "Bharati (Antarctica)", "coords": "69°24' S, 76°11' E", "status": "🟢 Operational (Year-Round)", "temp": "-9.8 °C (Annual Mean)"},
        {"name": "Himadri (Arctic)", "coords": "78°55' N, 11°56' E", "status": "🟢 Operational (Seasonal)", "temp": "-4.2 °C (Summer Season)"},
        {"name": "IndARC (Arctic Fjord)", "coords": "78°59' N, 12°01' E", "status": "🟢 Underwater Mooring", "temp": "Sub-surface hydrography"},
        {"name": "Dakshin Gangotri", "coords": "70°05' S, 12°00' E", "status": "⚪ Historic Monument", "temp": "Decommissioned 1990"}
    ]
    for s in stations_info:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.6); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #38BDF8;">
            <div style="display: flex; justify-content: space-between;">
                <strong>{s['name']}</strong>
                <span style="font-size: 0.8rem; color: #34D399;">{s['status']}</span>
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8;">Coords: {s['coords']} | Weather: {s['temp']}</div>
        </div>
        """, unsafe_allow_html=True)
