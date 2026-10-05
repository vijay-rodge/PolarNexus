import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
import pandas as pd
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config.settings import settings
from agents.tools.controlled_tools import ControlledPolarTools
from scientific_engine.schema_detector import SchemaDetector
from scientific_engine.validator import DataValidator

st.set_page_config(page_title="NPDC Datasets | NCPOR", page_icon="📊", layout="wide")
render_sidebar()

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 style="color: #38BDF8; margin: 0;">📊 National Polar Data Center (NPDC) Catalog</h2>
    <p style="color: #94A3B8; margin: 0.3rem 0;">Quality-controlled scientific datasets with automated schema detection and sensor validation</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    station_filter = st.selectbox("Filter by Station", ["All", "Maitri", "Bharati"])
with col2:
    domain_filter = st.selectbox("Filter by Scientific Domain", ["All", "Polar Meteorology & Climate Dynamics", "Oceanography & Marine Biogeochemistry"])

datasets = ControlledPolarTools.search_datasets(
    station_name=station_filter if station_filter != "All" else None,
    domain=domain_filter if domain_filter != "All" else None
)

st.write(f"Found **{len(datasets)}** registered scientific datasets:")

for ds in datasets:
    with st.expander(f"📁 {ds['title']} ({ds['temporal_resolution']})", expanded=True):
        st.markdown(f"""
        - **Dataset ID**: `{ds['dataset_id']}`
        - **Scientific Domain**: {ds['domain']}
        - **Temporal Coverage**: {ds['time_start']} to {ds['time_end']}
        - **Format**: {ds['file_format']} | **Size**: {ds.get('file_size_bytes', 0):,} bytes
        - **Citation**: {ds['citation']}
        - [Official NPDC Portal Page]({ds['npdc_access_url']})
        """)
        f_path = Path(ds['file_path']) if ds.get('file_path') else None
        if f_path and not f_path.exists():
            alt1 = settings.BASE_DIR / ds['file_path'].replace("\\", "/").lstrip("/")
            alt2 = settings.RAW_DATA_DIR / "aws" / f_path.name
            if alt1.exists():
                f_path = alt1
            elif alt2.exists():
                f_path = alt2
        if f_path and f_path.exists():
            df = pd.read_csv(f_path)
            schema = SchemaDetector.detect_schema(df)
            val_report = DataValidator.validate_dataset(df)

            st.markdown("#### 🔬 Automated Dataset Quality Report & Sensor Health")
            qcol1, qcol2, qcol3, qcol4 = st.columns(4)
            qcol1.metric("Total Observations", f"{schema['total_rows']:,}")
            qcol2.metric("Parameters (Cols)", f"{schema['total_columns']}")
            qcol3.metric("Completeness Score", f"{val_report['quality_score']*100:.1f}%")
            qcol4.metric("Duplicate Rows", f"{val_report['duplicate_rows']}")

            st.markdown("##### Parameter Schema:")
            schema_data = []
            for col_name, details in schema["column_details"].items():
                schema_data.append({
                    "Parameter Column": col_name,
                    "Type": details.get("type"),
                    "Inferred Unit": details.get("unit"),
                    "Missing %": f"{details.get('missing_percentage', 0)}%",
                    "Min Value": details.get("min", "N/A"),
                    "Max Value": details.get("max", "N/A"),
                    "Mean Value": details.get("mean", "N/A")
                })
            st.dataframe(pd.DataFrame(schema_data), use_container_width=True)

            st.markdown("##### First 5 Data Records:")
            st.dataframe(df.head(5), use_container_width=True)

            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"⬇️ Download Quality-Controlled CSV ({ds['dataset_id']})",
                data=csv_data,
                file_name=f"{ds['dataset_id']}.csv",
                mime='text/csv'
            )
        else:
            st.warning("Data file not stored locally.")
