import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from database.connection import SessionLocal
from database.models import Publication
from ml.classification.domain_classifier import ScientificDomainClassifier
from scientific_engine.document_analyzer import DocumentAnalyzer
from crawler.dspace_search_harvester import DSpaceSearchHarvester
from streamlit_app.components.sidebar import render_sidebar

st.set_page_config(page_title="PolarNexus | Publications Repository", page_icon="📄", layout="wide")
render_sidebar()

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 style="color: #38BDF8; margin: 0;">📄 NCPOR DSpace Scientific Publications Repository</h2>
    <p style="color: #94A3B8; margin: 0.3rem 0;">Peer-reviewed polar research articles indexed with automated ML domain classification, Geospatial Mapping & Live DSpace Search Harvester</p>
</div>
""", unsafe_allow_html=True)

tab_search, tab_crawled, tab_browse, tab_analyzer, tab_classifier = st.tabs([
    "🔍 Live DSpace Search & Pipeline (Search → Scrape → Ingest → Deep Synthesis)",
    "📥 Harvested Manuscripts & Expeditions",
    "📚 Institutional Publications",
    "🔬 Real-Time PDF / OCR Analyzer",
    "🤖 ML Domain Classifier"
])

# -------------------------------------------------------------
# TAB 1: Live DSpace Search & Automated Pipeline
# -------------------------------------------------------------
with tab_search:
    st.subheader("🔍 Live DSpace Simple-Search & Automated Systematic Pipeline")
    st.markdown("""
    Query the official **NCPOR DSpace Repository** (`http://14.139.119.23:8080/dspace/simple-search`). 
    The engine executes a systematic per-document processing loop:
    1. **Query DSpace search endpoint** and scrape matching item links.
    2. **Scrape Dublin Core metadata** and retrieve PDF bitstream links from the 'Files in This Item' table.
    3. **Download PDF manuscripts**, sanitize magic bytes (`%PDF-`), and compute SHA-256.
    4. **Extract page-by-page text** and generate RAG semantic chunks saved to `document_chunks.jsonl`.
    5. **Extract geodetic coordinates & diagrams** for interactive maps and figure galleries.
    6. **Synthesize extensive, deep scientific reports** specifically derived from each document's text.
    """)

    st.markdown("##### 🚀 Quick Search Presets:")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    preset_query = None
    if col_p1.button("🌊 Oceanology (Items 281 & 754)", use_container_width=True):
        preset_query = "oceanology"
    if col_p2.button("📍 Position Fixing (Item 133)", use_container_width=True):
        preset_query = "position fixing"
    if col_p3.button("🧪 Chemical Oceanography (Item 1142)", use_container_width=True):
        preset_query = "chemical oceanographic"
    if col_p4.button("❄️ Maitri Meteorology (Item 128)", use_container_width=True):
        preset_query = "meteorology"

    # Search bar input
    default_search_val = preset_query if preset_query else st.session_state.get("last_dspace_query", "oceanology")
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        search_kw = st.text_input("Enter DSpace search keyword or research topic:", value=default_search_val, key="dspace_search_kw")
    with col_btn:
        st.write("")
        st.write("")
        execute_search = st.button("🚀 Search DSpace & Run Pipeline", type="primary", use_container_width=True)

    if (execute_search or preset_query) and search_kw:
        st.session_state.last_dspace_query = search_kw
        with st.status(f"Executing Automated Ingestion Loop for '{search_kw}'...", expanded=True) as status:
            st.write(f"📡 Step 1: Querying DSpace simple-search: `http://14.139.119.23:8080/dspace/simple-search?query={search_kw}`")
            harvester = DSpaceSearchHarvester()
            st.write("📑 Step 2: Scraping search hits and parsing Dublin Core / bitstream tables...")
            st.write("📥 Step 3: Downloading PDF files and verifying SHA-256 / %PDF- magic bytes...")
            st.write("✂️ Step 4: Extracting text page-by-page and generating RAG chunks...")
            st.write("🗺️ Step 5: Parsing geodetic coordinates and extracting visual figure charts...")
            st.write("🤖 Step 6: Generating deep, non-hallucinated scientific synthesis for each manuscript...")
            harvest_result = harvester.search_and_harvest(query=search_kw, max_items=5, download_pdfs=True)
            st.session_state.last_harvest_result = harvest_result
            status.update(label=f"✅ Pipeline Completed: Processed {len(harvest_result['harvested_items'])} Documents for '{search_kw}'!", state="complete")

    # Render results if available in session_state
    if "last_harvest_result" in st.session_state:
        res = st.session_state.last_harvest_result
        st.success(f"✨ Successfully executed DSpace pipeline for **'{res['query']}'** | Found **{res['total_hits']}** hits | Ingested **{len(res['harvested_items'])}** PDFs | Generated **{res['total_chunks_saved']}** RAG Chunks!")

        # Consolidated Summary & Overview
        st.markdown("---")
        st.markdown("### 🧭 Multi-Expedition Scientific Overview")
        st.markdown(f"""
        The automated search identified **{len(res['harvested_items'])} verified research manuscripts** in the NCPOR DSpace Repository.
        Each document has been systematically scraped, verified, chunked for RAG, and analyzed. Below is the dedicated extensive scientific report, interactive map, and figure gallery for each paper.
        """)

        # Consolidated Coordinates Map
        coords = res.get("coordinates", [])
        if coords:
            st.markdown(f"#### 🗺️ Consolidated Survey Map ({len(coords)} Extracted Locations across All Hits)")
            map_df = pd.DataFrame([{"lat": float(c["latitude"]), "lon": float(c["longitude"])} for c in coords if "latitude" in c and "longitude" in c])
            if not map_df.empty:
                st.map(map_df, zoom=3)
            c_df = pd.DataFrame(coords)
            cols_show = [col for col in ["name", "station", "dms_lat", "dms_lon", "latitude", "longitude", "elevation_m", "datum"] if col in c_df.columns]
            st.dataframe(c_df[cols_show], use_container_width=True)

        # Consolidated Figures Gallery
        figs = res.get("extracted_figures", [])
        if figs:
            st.markdown(f"#### 🖼️ Consolidated Media Gallery ({len(figs)} Visual Assets Extracted)")
            f_cols = st.columns(min(len(figs), 3))
            for i, f in enumerate(figs):
                with f_cols[i % len(f_cols)]:
                    st.image(f["file_path"], caption=f.get("caption", f"Figure {i+1}"), use_container_width=True)

        # SYSTEMATIC PER-DOCUMENT LOOP: Render extensive report for EACH paper!
        st.markdown("---")
        st.markdown("## 📚 Individual Manuscript Deep Analysis (Systematic Per-Item Loop)")

        for idx, item in enumerate(res.get("harvested_items", []), 1):
            with st.container():
                st.markdown(f"### 📑 [{idx}/{len(res['harvested_items'])}] {item.get('title')}")
                col_m1, col_m2 = st.columns([2, 1])
                with col_m1:
                    st.markdown(f"**Author(s)**: {item.get('authors', 'N/A')}")
                    st.markdown(f"**Collection / Field**: {item.get('collection', 'N/A')}")
                    st.markdown(f"**Issue Date**: {item.get('issue_date', 'N/A')}")
                    if item.get("handle_url"):
                        st.markdown(f"[🔗 View in NCPOR DSpace Repository]({item['handle_url']})")
                    if item.get("primary_pdf_url"):
                        st.markdown(f"[📥 Original Bitstream PDF]({item['primary_pdf_url']})")
                with col_m2:
                    st.markdown(f"**Item ID**: `{item.get('item_id')}`")
                    st.markdown(f"**Download Status**: `{item.get('download_status')}`")
                    st.markdown(f"**Pages**: `{item.get('total_pages', 0)}` | **Chars**: `{item.get('total_characters', 0):,}`")
                    st.markdown(f"**RAG Chunks Generated**: `{item.get('chunks_count', 0)}`")
                    if item.get("file_size_bytes"):
                        st.markdown(f"**File Size**: {item['file_size_bytes']:,} bytes")

                # Detailed Synthesis for this document
                detailed_text = item.get("detailed_synthesis")
                if not detailed_text:
                    detailed_text = DocumentAnalyzer.generate_detailed_document_synthesis(
                        text=item.get("extracted_text", ""),
                        metadata=item
                    )
                st.markdown(detailed_text)

                # Document-specific coordinates map
                item_coords = item.get("coordinates", [])
                if item_coords:
                    with st.expander(f"🗺️ View Extracted Coordinates for Document [{idx}] ({len(item_coords)} Points)", expanded=True):
                        i_map_df = pd.DataFrame([{"lat": float(c["latitude"]), "lon": float(c["longitude"])} for c in item_coords if "latitude" in c and "longitude" in c])
                        if not i_map_df.empty:
                            st.map(i_map_df, zoom=4)
                        i_c_df = pd.DataFrame(item_coords)
                        cols_s = [col for col in ["name", "station", "dms_lat", "dms_lon", "latitude", "longitude", "elevation_m", "datum"] if col in i_c_df.columns]
                        st.dataframe(i_c_df[cols_s], use_container_width=True)

                # Document-specific figures gallery
                item_figs = item.get("extracted_figures", [])
                if item_figs:
                    with st.expander(f"🖼️ View Isolated Diagrams & Charts for Document [{idx}] ({len(item_figs)} Assets)", expanded=True):
                        if_cols = st.columns(min(len(item_figs), 3))
                        for f_i, fig in enumerate(item_figs):
                            with if_cols[f_i % len(if_cols)]:
                                st.image(fig["file_path"], caption=fig.get("caption", f"Figure {f_i+1}"), use_container_width=True)

                # RAG chunks viewer
                if item.get("extracted_text"):
                    with st.expander(f"📄 View Extracted Text Chunks for Document [{idx}]"):
                        st.text_area(f"Full Text for {item.get('item_id')}", item["extracted_text"][:3000], height=220)

                st.markdown("---")

# -------------------------------------------------------------
# TAB 2: Harvested Manuscripts & Expeditions
# -------------------------------------------------------------
with tab_crawled:
    st.subheader("📥 DSpace Harvested Manuscripts & Expeditions")
    st.markdown("Displays research papers, technical reports, and bitstreams harvested directly from the live NCPOR DSpace repository.")

    docs_json_file = root_dir / "data" / "metadata" / "documents.json"
    crawled_docs = []
    if docs_json_file.exists():
        try:
            with open(docs_json_file, "r", encoding="utf-8") as f:
                crawled_docs = json.load(f)
        except Exception:
            crawled_docs = []

    if not crawled_docs:
        st.info("No crawled documents found in `data/metadata/documents.json`. Run the crawler via CLI or Tab 1 to harvest items!")
    else:
        st.write(f"Displaying **{len(crawled_docs)}** harvested documents from NCPOR DSpace:")
        for idx, doc in enumerate(crawled_docs, 1):
            with st.expander(f"📑 [{idx}] {doc.get('title', 'Untitled')} ({doc.get('year', 'N/A')})", expanded=(idx == 1)):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Item ID**: `{doc.get('item_id')}`")
                    st.markdown(f"**Authors**: {doc.get('authors', 'N/A')}")
                    st.markdown(f"**Expedition**: {doc.get('expedition', 'N/A')}")
                    st.markdown(f"**Collection**: {doc.get('collection', 'N/A')}")
                    st.markdown(f"**Keywords**: {', '.join(doc.get('keywords', [])) if doc.get('keywords') else 'N/A'}")
                    if doc.get('handle_url'):
                        st.markdown(f"[🔗 View in NCPOR DSpace Repository]({doc['handle_url']})")
                    if doc.get('primary_pdf_url'):
                        st.markdown(f"[📥 Original Bitstream PDF]({doc['primary_pdf_url']})")

                with col2:
                    st.markdown(f"**Download Status**: `{doc.get('download_status', 'pending')}`")
                    st.markdown(f"**Extraction Status**: `{doc.get('extraction_status', 'pending')}`")
                    if doc.get('file_size_bytes'):
                        st.markdown(f"**File Size**: {doc['file_size_bytes']:,} bytes")
                    if doc.get('sha256'):
                        st.markdown(f"**SHA-256**: `{doc['sha256'][:16]}...`")

                # Dropdown for Geodetic Coordinates and Interactive Map
                coords = doc.get("coordinates", [])
                if not coords and doc.get("item_id"):
                    item_json_path = root_dir / "data" / "extracted" / f"{doc['item_id']}.json"
                    if item_json_path.exists():
                        try:
                            with open(item_json_path, "r", encoding="utf-8") as f_j:
                                item_data = json.load(f_j)
                                coords = item_data.get("coordinates", [])
                        except Exception:
                            pass

                if coords:
                    with st.expander("🗺️ View Extracted Geodetic Coordinates & Survey Map", expanded=False):
                        st.markdown("##### 📍 Verified Geodetic Benchmark Coordinates")
                        c_df = pd.DataFrame(coords)
                        cols_to_show = [c for c in ["name", "station", "dms_lat", "dms_lon", "latitude", "longitude", "elevation_m", "datum"] if c in c_df.columns]
                        st.dataframe(c_df[cols_to_show], use_container_width=True)

                        map_data = [{"lat": float(c["latitude"]), "lon": float(c["longitude"])} for c in coords if "latitude" in c and "longitude" in c]
                        if map_data:
                            st.map(pd.DataFrame(map_data), zoom=7)

                # Dropdown for Extracted Figures and Diagram Gallery
                figures = doc.get("extracted_figures", [])
                if not figures and doc.get("item_id"):
                    item_json_path = root_dir / "data" / "extracted" / f"{doc['item_id']}.json"
                    if item_json_path.exists():
                        try:
                            with open(item_json_path, "r", encoding="utf-8") as f_j:
                                item_data = json.load(f_j)
                                figures = item_data.get("figures", [])
                        except Exception:
                            pass

                if figures:
                    with st.expander("🖼️ View Extracted Figures & Diagram Gallery", expanded=False):
                        st.markdown("##### 🖼️ Extracted Polar Figures, Satellite Geometry & Maps")
                        f_cols = st.columns(min(len(figures), 3))
                        for f_idx, fig in enumerate(figures):
                            with f_cols[f_idx % len(f_cols)]:
                                st.image(fig["file_path"], caption=fig.get("caption", f"Figure {f_idx+1}"), use_container_width=True)

                # Dropdown for Extracted Plain Text & Chunks
                txt_path = root_dir / "data" / "extracted" / f"{doc.get('item_id')}.txt"
                if txt_path.exists():
                    with st.expander("📄 View Extracted Plain Text"):
                        st.text_area(f"Text for {doc.get('item_id')}", txt_path.read_text(encoding='utf-8', errors='ignore')[:3000], height=200)

# -------------------------------------------------------------
# TAB 3: Institutional Publications
# -------------------------------------------------------------
with tab_browse:
    db = SessionLocal()
    try:
        pubs = db.query(Publication).all()
    finally:
        db.close()

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        search_query = st.text_input("Search Publications by Keyword, Author, or Title", "")
    with col_s2:
        domains = ["All"] + sorted(list({p.domain for p in pubs if p.domain}))
        selected_domain = st.selectbox("Filter by Domain", domains)

    filtered_pubs = pubs
    if search_query:
        term = search_query.lower()
        filtered_pubs = [p for p in filtered_pubs if term in p.title.lower() or term in p.authors.lower() or term in (p.abstract or "").lower()]

    if selected_domain != "All":
        filtered_pubs = [p for p in filtered_pubs if p.domain == selected_domain]

    st.write(f"Displaying **{len(filtered_pubs)}** research papers:")

    for p in filtered_pubs:
        with st.expander(f"📚 {p.title} ({p.year})"):
            st.markdown(f"**Authors**: {p.authors}")
            st.markdown(f"**Journal**: *{p.journal_name}* | **DOI**: `{p.doi}`")
            st.markdown(f"**Domain**: `{p.domain}`")
            st.markdown(f"**Abstract**:\n{p.abstract}")
            st.markdown(f"[🔗 View in NCPOR DSpace Institutional Repository]({p.dspace_handle_url})")

# -------------------------------------------------------------
# TAB 4: Real-Time PDF / OCR Analyzer
# -------------------------------------------------------------
with tab_analyzer:
    st.subheader("🔬 Real-Time Polar Manuscript / OCR Text Analyzer")
    sample_default = """POLAR ORBIT (1) 108 MIN POLAR ORBIT (2) Position Fixing in Antarctica M. C.Pathak1 ABSTRACT Antarctica with large desolate areas, snow and ice cover, few land marks, hostile weather and bad radio propagation conditions poses problems for position fixing. The Expedition used a portable land sea satellite position fixing system and least square and 3 D techniques to determine the following positions: Automatic Weather Station, Dakshin Gangotri Base Camp (Hut) Base Camp - 70o45' 12". 963S: 11o38' 13".618E - 69°59'12".672S:11°55'7".263E - 69°59'23".119S: H°56'26".83E The positions obtained were within a few metres."""
    ocr_input = st.text_area("Polar Document OCR Snippet", sample_default, height=180)

    if st.button("🚀 Analyze Manuscript & Extract Geodesy", type="primary"):
        with st.spinner("Extracting coordinates, correcting OCR noise & generating executive summary..."):
            extracted_coords = DocumentAnalyzer.extract_geodetic_coordinates(ocr_input)
            exec_summary = DocumentAnalyzer.generate_executive_summary(ocr_input, "Position Fixing in Antarctica")

            st.success(f"Successfully extracted {len(extracted_coords)} geodetic survey coordinates!")

            if extracted_coords:
                st.markdown("### 🗺️ Interactive Antarctic Survey Map")
                map_df = pd.DataFrame([{"lat": c["latitude"], "lon": c["longitude"]} for c in extracted_coords])
                st.map(map_df, zoom=7)

                st.markdown("### 📍 Survey Coordinate Benchmark Table")
                c_df = pd.DataFrame(extracted_coords)
                st.dataframe(c_df[["name", "station", "dms_lat", "dms_lon", "latitude", "longitude", "elevation_m", "datum"]], use_container_width=True)

            st.markdown("### 📑 Synthesized Scientific Executive Summary")
            st.markdown(exec_summary)

# -------------------------------------------------------------
# TAB 5: ML Domain Classifier
# -------------------------------------------------------------
with tab_classifier:
    st.subheader("🤖 Scikit-Learn Polar Research Domain Classification")
    sample_abstract = st.text_area(
        "Abstract Text Input",
        "Continuous ice core drilling conducted at 200m depth revealed paleoclimatic temperature oscillations and volcanic ash layers over the past 50,000 years."
    )

    if st.button("Predict Research Domain"):
        pred = ScientificDomainClassifier.predict(sample_abstract)
        st.success(f"**Predicted Domain**: {pred['predicted_domain']} (Confidence: {pred['confidence']*100:.1f}%)")
        st.markdown("##### Probabilities Across Domains:")
        for d, prob in pred['top_probabilities']:
            st.markdown(f"- **{d}**: {prob*100:.2f}%")
