import streamlit as st
import pandas as pd
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.graph import execute_polar_query
from streamlit_app.components.citations import render_citations_drawer
from streamlit_app.components.charts import render_timeseries_chart
from streamlit_app.components.sidebar import render_sidebar

st.set_page_config(page_title="PolarNexus | AI Assistant", page_icon="🤖", layout="wide")
render_sidebar()

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 style="color: #38BDF8; margin: 0;">🤖 Intelligent Polar Science Assistant</h2>
    <p style="color: #94A3B8; margin: 0.3rem 0;">LangGraph Dynamic Routing: RAG Documents + Sandboxed Scientific Data Analysis + Media Discovery</p>
</div>
""", unsafe_allow_html=True)

st.markdown("##### 🚀 Benchmark Query Presets:")
cols = st.columns(4)
q_preset = None

if cols[0].button("🌡️ Maitri Temp 2012", use_container_width=True):
    q_preset = "What was the average temperature at Maitri in 2012?"
if cols[1].button("❄️ About Maitri Station", use_container_width=True):
    q_preset = "Tell me about Maitri station."
if cols[2].button("🚢 15th Arctic Expedition", use_container_width=True):
    q_preset = "What research was conducted during the 15th Arctic Expedition?"
if cols[3].button("🎓 School Student Guide", use_container_width=True):
    q_preset = "Explain India's Antarctic research to a school student."

cols2 = st.columns(4)
if cols2[0].button("📊 Datasets at Maitri", use_container_width=True):
    q_preset = "What datasets are available for Maitri?"
if cols2[1].button("📸 Bharati Photos", use_container_width=True):
    q_preset = "Show me photographs of Bharati station."
if cols2[2].button("📍 Dakshin Gangotri Geodesy", use_container_width=True):
    q_preset = "Tell me about Dakshin Gangotri station and position fixing coordinates."
if cols2[3].button("🛡️ Out-of-Domain Safety Test", use_container_width=True):
    q_preset = "Who won the 2022 FIFA World Cup in Qatar?"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        if msg.get("route"):
            badge_color = "#0284C7" if msg["route"] == "DOCUMENT_RAG" else "#10B981" if msg["route"] == "SCIENTIFIC_DATA_ANALYSIS" else "#F59E0B"
            resp_ms = msg.get("response_time_ms", 0.0)
            st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; margin-bottom: 0.8rem; align-items: center;">
                <span style="background: {badge_color}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                    ROUTE: {msg['route']}
                </span>
                <span style="background: rgba(255,255,255,0.1); color: #E2E8F0; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem;">
                    INTENT: {msg.get('intent', 'GENERAL')}
                </span>
                <span style="background: #0F766E; color: #5EEAD4; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                    ⚡ {resp_ms:.1f} ms
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(msg["content"])

        # Render Geodetic Coordinates Map
        if msg.get("coordinates"):
            coords = msg["coordinates"]
            st.markdown("#### 🗺️ Extracted Geodetic Survey Benchmark Coordinates")
            map_data = [{"lat": float(c["latitude"]), "lon": float(c["longitude"])} for c in coords if "latitude" in c and "longitude" in c]
            if map_data:
                st.map(pd.DataFrame(map_data), zoom=7)
            coord_df = pd.DataFrame(coords)
            cols_to_show = [col for col in ["name", "station", "dms_lat", "dms_lon", "latitude", "longitude", "elevation_m", "datum"] if col in coord_df.columns]
            st.dataframe(coord_df[cols_to_show], use_container_width=True)

        # Render Extracted Figures
        if msg.get("extracted_figures"):
            figs = msg["extracted_figures"]
            st.markdown("#### 🖼️ Extracted Publication Figures & Maps")
            fig_cols = st.columns(min(len(figs), 3))
            for i, f in enumerate(figs):
                with fig_cols[i % len(fig_cols)]:
                    st.image(f["file_path"], caption=f.get("caption", f"Figure {i+1}"), use_container_width=True)

        # Render Timeseries Chart
        if msg.get("chart_df") is not None:
            render_timeseries_chart(
                df=msg["chart_df"],
                parameter_col=msg.get("chart_param", "air_temperature"),
                time_col="timestamp",
                title=msg.get("chart_title", "Observation Time-Series")
            )

        # Render Citations
        if msg.get("citations"):
            render_citations_drawer(msg["citations"])

user_input = st.chat_input("Ask any scientific, data, expedition, or historical polar question...")
active_query = q_preset if q_preset else user_input

if active_query:
    st.session_state.chat_messages.append({"role": "user", "content": active_query})
    with st.chat_message("user"):
        st.markdown(active_query)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing intent, routing pipeline & validating scientific citations..."):
            result = execute_polar_query(active_query)
            
            final_ans = result.get("final_answer", "")
            citations = result.get("citations", [])
            intent = result.get("intent", "GENERAL")
            route = result.get("route", "GENERAL")
            data_res = result.get("data_analysis_result")
            coords = result.get("coordinates", [])
            figs = result.get("extracted_figures", [])
            resp_time = result.get("response_time_ms", 0.0)

            badge_color = "#0284C7" if route == "DOCUMENT_RAG" else "#10B981" if route == "SCIENTIFIC_DATA_ANALYSIS" else "#F59E0B"
            st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; margin-bottom: 0.8rem; align-items: center;">
                <span style="background: {badge_color}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                    ROUTE: {route}
                </span>
                <span style="background: rgba(255,255,255,0.1); color: #E2E8F0; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem;">
                    INTENT: {intent}
                </span>
                <span style="background: #0F766E; color: #5EEAD4; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                    ⚡ {resp_time:.1f} ms
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(final_ans)

            # Interactive Coordinates Map
            if coords:
                st.markdown("#### 🗺️ Extracted Geodetic Survey Benchmark Coordinates")
                map_data = [{"lat": float(c["latitude"]), "lon": float(c["longitude"])} for c in coords if "latitude" in c and "longitude" in c]
                if map_data:
                    st.map(pd.DataFrame(map_data), zoom=7)
                coord_df = pd.DataFrame(coords)
                cols_to_show = [col for col in ["name", "station", "dms_lat", "dms_lon", "latitude", "longitude", "elevation_m", "datum"] if col in coord_df.columns]
                st.dataframe(coord_df[cols_to_show], use_container_width=True)

            # Extracted Figures
            if figs:
                st.markdown("#### 🖼️ Extracted Publication Figures & Maps")
                fig_cols = st.columns(min(len(figs), 3))
                for i, f in enumerate(figs):
                    with fig_cols[i % len(fig_cols)]:
                        st.image(f["file_path"], caption=f.get("caption", f"Figure {i+1}"), use_container_width=True)

            chart_df = None
            chart_param = "air_temperature"
            chart_title = ""

            if data_res and data_res.get("success"):
                csv_path = None
                st_name = data_res.get("station", "").lower()
                yr = data_res.get("year", 2012)
                
                for f in (root_dir / "data" / "raw" / "aws").glob("*.csv"):
                    if st_name in f.name.lower() and str(yr) in f.name:
                        csv_path = f
                        break
                
                if csv_path and csv_path.exists():
                    chart_df = pd.read_csv(csv_path)
                    chart_param = data_res.get("parameter", "air_temperature")
                    chart_title = f"{data_res.get('station')} AWS Observation Record ({yr})"
                    render_timeseries_chart(
                        df=chart_df,
                        parameter_col=chart_param,
                        time_col="timestamp",
                        title=chart_title,
                        unit=data_res.get("unit", "°C")
                    )

            if citations:
                render_citations_drawer(citations)

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": final_ans,
                "route": route,
                "intent": intent,
                "response_time_ms": resp_time,
                "coordinates": coords,
                "extracted_figures": figs,
                "citations": citations,
                "chart_df": chart_df,
                "chart_param": chart_param,
                "chart_title": chart_title
            })
