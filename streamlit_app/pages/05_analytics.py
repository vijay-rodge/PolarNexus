import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
import pandas as pd
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from scientific_engine.analyzer import ScientificDataAnalyzer
from streamlit_app.components.charts import render_timeseries_chart, render_monthly_distribution_chart
from config.settings import settings

st.set_page_config(page_title="Scientific Analytics Studio | NCPOR", page_icon="📈", layout="wide")
render_sidebar()

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 style="color: #38BDF8; margin: 0;">📈 Scientific Data & Polar Meteorology Studio</h2>
    <p style="color: #94A3B8; margin: 0.3rem 0;">High-frequency Automatic Weather Station (AWS) observations from Maitri and Bharati</p>
</div>
""", unsafe_allow_html=True)

aws_dir = settings.RAW_DATA_DIR / "aws"
csv_files = list(aws_dir.glob("*.csv"))

if not csv_files:
    st.error("No AWS CSV datasets discovered.")
    st.stop()

file_names = [f.name for f in csv_files]
selected_file = st.selectbox("Select Station AWS Dataset", file_names)

selected_path = aws_dir / selected_file
df = pd.read_csv(selected_path)
df["timestamp"] = pd.to_datetime(df["timestamp"])

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
with col_ctrl1:
    num_cols = [c for c in df.columns if c not in ["timestamp", "station"]]
    selected_param = st.selectbox("Select Parameter", num_cols, index=0)

with col_ctrl2:
    selected_op = st.selectbox("Aggregation Operation", ["mean", "min", "max", "std", "monthly_average", "trend_slope"])

with col_ctrl3:
    date_min = df["timestamp"].min().date()
    date_max = df["timestamp"].max().date()
    date_range = st.date_input("Date Range", [date_min, date_max])

filtered_df = df
if len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = df[(df["timestamp"].dt.date >= start_d) & (df["timestamp"].dt.date <= end_d)]

st.markdown("---")

calc_result = ScientificDataAnalyzer.execute_analysis(
    df=filtered_df,
    parameter=selected_param,
    operation=selected_op,
    station_name=selected_file.split("_")[0].capitalize(),
    dataset_title=selected_file
)

res_col1, res_col2 = st.columns([1, 2])
with res_col1:
    st.markdown("### 🧮 Programmatic Calculation")
    if calc_result.get("success"):
        st.metric(
            label=f"{selected_op.upper()} {selected_param}",
            value=f"{calc_result.get('calculated_value')} {calc_result.get('unit')}",
            help="Computed with vectorized Pandas aggregation. Sandboxed execution."
        )
        st.caption(f"Sample Count: {calc_result.get('sample_size'):,} observations")
        st.json(calc_result.get("details"))
    else:
        st.error(calc_result.get("error"))

with res_col2:
    st.markdown("### 📊 Distribution & Summary Statistics")
    st.dataframe(filtered_df[selected_param].describe().to_frame().T, use_container_width=True)

st.markdown("### 📉 High-Resolution Observation Time-Series")
render_timeseries_chart(
    df=filtered_df,
    parameter_col=selected_param,
    time_col="timestamp",
    title=f"{selected_file} — {selected_param.replace('_', ' ').title()}",
    unit=calc_result.get("unit", "")
)

st.markdown("### 📅 Monthly Polar Seasonal Distribution")
render_monthly_distribution_chart(
    df=filtered_df,
    parameter_col=selected_param,
    time_col="timestamp",
    title=f"Monthly Variations: {selected_param}",
    unit=calc_result.get("unit", "")
)
