# ❄️ NCPOR Polar Science Outreach, Knowledge Repository & Media Dissemination Portal

**Problem Statement ID: 26063**  
**National Centre for Polar and Ocean Research (NCPOR) / Ministry of Earth Sciences (MoES)**  
**Platform**: Integrated Industry-Level Polar Science Knowledge Base (RAG + LangGraph + ML + Scientific Analytics + DSpace Harvester)

---

## 🧭 Executive Overview

The **Integrated Polar Science Outreach and Knowledge Repository** is a production-grade scientific platform designed for the Arctic, Antarctic, and Southern Ocean research programs.

It combines:
1. **LangGraph Multi-Agent Dynamic Router**: Directs user queries intelligently between Document RAG, Sandboxed Scientific Data Analysis, Media Discovery, and Domain Cataloging.
2. **Deterministic Scientific Data Analysis Engine**: Never asks LLMs to calculate math. Computes meteorological parameters (e.g. AWS 2012 Maitri air temperatures) via Pandas vectorized routines with zero hallucination.
3. **Automated Geodetic Coordinate & Map Pipeline**: Scans scientific publications, normalizes historical OCR anomalies, extracts precise survey coordinates (DMS & Decimal) and antenna elevations, and plots interactive geospatial Antarctic maps.
4. **Visual Figure & Media Harvester**: Isolates high-resolution scientific diagrams, orbital schematics, and expedition maps from manuscript bitstreams.
5. **NCPOR DSpace Harvester**: Connects directly to the official NCPOR DSpace Institutional Repository (`http://14.139.119.23:8080/dspace/`), extracting Dublin Core metadata and PDF manuscripts.
6. **ML Governance & Domain Classification**: Scikit-Learn TF-IDF classifier for peer-reviewed abstract categorisation with versioned metadata registry tracking.

---

## 🏗️ System Architecture

```text
                                USER QUERY
                                    │
                                    ▼
                          LANGGRAPH ROUTER
                                    │
        ┌───────────────────┬───────┴───────────┬───────────────────┐
        ▼                   ▼                   ▼                   ▼
  TEXT / DOCUMENT      STRUCTURED AWS        MEDIA & PHOTO      EDUCATIONAL
     PIPELINE          DATA ANALYSIS            GALLERY          OUTREACH
        │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼
    CHROMA RAG         PANDAS ENGINE        METADATA DB         SIMPLIFIED
  (Vector Search)   (Zero-Hallucination) (Extracted Figures)   EXPLANATIONS
        │                   │                   │                   │
        └───────────────────┼───────────────────┴───────────────────┘
                            │
                            ▼
              RAW RETRIEVED SCIENTIFIC EVIDENCE
                            │
                            ▼
                SYNTHESIZED SCIENTIFIC OUTPUT
              (Citations + Maps + Media Assets)
```

---

## 📍 Key Benchmark Capabilities

### 1. Geodetic Position Fixing in Antarctica (1st Indian Antarctic Expedition)
- **Paper**: *Position Fixing in Antarctica* (M. C. Pathak)
- **DSpace Handle**: `http://hdl.handle.net/123456789/133`
- **Extracted Survey Coordinates**:
  - **Automatic Weather Station (Dakshin Gangotri)**: `70° 45' 12.963" S`, `11° 38' 13.618" E` (Elevation: **150.12 m**)
  - **First Indian Base Camp (Hut)**: `69° 59' 12.672" S`, `11° 55' 07.263" E` (Elevation: **35.00 m**)
  - **Base Camp (Ice Shelf Edge)**: `69° 59' 23.119" S`, `11° 56' 26.830" E` (Elevation: **44.25 m**)
- **Extracted Visual Figures**:
  - Figure 1: Orbital geometry and polar transit trajectories of Doppler navigation satellites
  - Figure 2: Polar orbital constellation coverage over high-latitude Antarctic coordinates
  - Figure 3: Full high-resolution survey map of positions fixed in Queen Maud Land
  - Figure 4 & 5: Field deployment of JMR Doppler receiver and coordinate terminal printout

### 2. AWS Scientific Data Analysis (Maitri 2012)
- Query: *"What was the average temperature at Maitri in 2012?"*
- **Result**: `-10.38 °C` (Min: `-34.50 °C`, Max: `+7.80 °C`, Sample: 8,784 hourly quality-controlled readings).
- Provenance: Deterministic execution via pandas aggregation with zero generative math guessing.

---

## 📁 Repository Structure

```text
prototype_2/
├── agents/                     # LangGraph multi-agent cognitive architecture
│   ├── graph.py                # Graph compilation, edges, conditional routing
│   ├── state.py                # QueryState definition (coordinates, figures, trace)
│   ├── nodes/                  # Agent nodes (classify, normalize, retrieve, generate, validate)
│   └── tools/                  # Controlled tools for DB, vectorstore, analysis
├── api/                        # FastAPI REST backend
│   └── main.py                 # Health, query, dataset, and analytics endpoints
├── config/                     # Application configurations & environment settings
│   └── settings.py             # Pydantic BaseSettings
├── connectors/                 # External repository harvesters
│   ├── base.py                 # Abstract harvester interface
│   └── dspace_harvester.py     # Live crawler for NCPOR DSpace Institutional Repository
├── data/                       # Data persistence layer
│   ├── metadata/               # ML model governance & JSON registries
│   ├── raw/aws/                # Cleaned AWS meteorological CSVs (Maitri 2012)
│   ├── raw/media/              # Official photos & extracted publication figures
│   ├── raw/publications/       # Downloaded scientific PDFs & analysis cache JSONs
│   ├── vectorstore/chroma/     # ChromaDB persistent vector database
│   └── polar_science.db        # SQLite / PostgreSQL relational database
├── database/                   # SQLAlchemy database ORM
│   ├── connection.py           # Database engine & SessionLocal factory
│   ├── models.py               # Station, Expedition, Dataset, Publication, MediaRecord models
│   └── seed_data.py            # Comprehensive initial seed data for polar repository
├── ml/                         # Machine learning models & governance
│   ├── classification/         # Domain classifier (TF-IDF + Logistic Regression)
│   └── registry/               # Model registry & performance tracker
├── scientific_engine/          # High-performance scientific analysis & extraction
│   ├── analyzer.py             # Meteorological aggregation & pandas statistics
│   ├── document_analyzer.py    # Geodetic coordinate extraction, figure isolation, synthesis
│   ├── schema_detector.py      # Automated CSV dialect and column detector
│   ├── validator.py            # Quality control & outlier detection
│   └── visualizer.py           # Plotly interactive polar charts
├── streamlit_app/              # Streamlit frontend user interface
│   ├── app.py                  # Main entry point & platform landing page
│   └── pages/                  # Multipage dashboard
│       ├── 01_assistant.py     # Polar AI Assistant with interactive map & figure gallery
│       ├── 02_stations.py      # Station Explorer (Maitri, Bharati, Himadri, Dakshin Gangotri)
│       ├── 03_expeditions.py   # Expedition Explorer (Antarctic & Arctic missions)
│       ├── 04_datasets.py      # NPDC Dataset metadata catalog & schema inspector
│       ├── 05_analytics.py     # Interactive meteorological analytics dashboard
│       ├── 06_publications.py  # DSpace Publications, Coordinates Map & Live PDF Analyzer
│       ├── 07_media.py         # Curated photo gallery & technical diagrams
│       ├── 08_outreach.py      # Educational guides, polar trivia & school portal
│       └── 09_admin.py         # Ingestion monitoring, harvest logs & ML governance
└── tests/                      # Pytest automated test suite (18 test cases)
    ├── test_document_analyzer.py
    ├── test_langgraph.py
    ├── test_ml_models.py
    ├── test_rag_pipeline.py
    └── test_scientific_engine.py
```

---

## 🛠️ Quickstart Installation & Setup

### 1. Prerequisites
- **Python 3.11+**
- Virtual environment (recommended)

### 2. Environment Setup
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database & Vector Store
```powershell
python scripts/run_setup.py
```

### 4. Launch the Streamlit Portal
```powershell
streamlit run streamlit_app/app.py
```
Access the application at `http://localhost:8501`.

### 5. Launch FastAPI Backend (Optional)
```powershell
uvicorn api.main:app --reload --port 8000
```
Interactive API docs at `http://127.0.0.1:8000/docs`.

### 6. Run the Test Suite
```powershell
pytest tests/ -v
```
All 18 automated tests will run and report pass status.

---

## 🏛️ Polar Research Stations Covered

| Station Name | Region | Coordinates | Commissioned | Operational Status |
| :--- | :--- | :--- | :--- | :--- |
| **Maitri** | Schirmacher Oasis, Antarctica | 70° 45' 58" S, 11° 43' 56" E | 1989 | Active (Year-Round) |
| **Bharati** | Larsemann Hills, Antarctica | 69° 24' 28" S, 76° 11' 14" E | 2012 | Active (Year-Round) |
| **Dakshin Gangotri** | Ice Shelf, Antarctica | 70° 45' 12" S, 11° 38' 13" E | 1983 | Decommissioned (Historical Datum) |
| **Himadri** | Ny-Ålesund, Svalbard, Arctic | 78° 55' 00" N, 11° 56' 00" E | 2008 | Active (Seasonal / Summer) |
| **IndARC** | Kongsfjorden, Arctic | 78° 59' 00" N, 11° 49' 00" E | 2014 | Active (Underwater Observatory) |
| **Himansh** | Chandra Basin, Western Himalaya | 32° 24' 00" N, 77° 37' 00" E | 2016 | Active (High-Altitude Cryosphere) |

---


---

## 🕷️ Resumable NCPOR DSpace Crawler & Ingestion Pipeline

A production-grade, state-persisted crawler designed specifically for the official NCPOR DSpace Institutional Repository (http://14.139.119.23:8080/dspace/).

### Features:
- **Resumable SQLite State Manager**: Uses data/crawler_state.db to track discovered, queued, visited, failed, and restricted URLs. If interrupted, resumes seamlessly without duplicating work.
- **Hierarchical Graph Traversal**: Automatically traverses nested Community → Collection → Item pages, preserving the full scientific hierarchy.
- **Strict PDF Binary Verification**: Streams downloads, resolves HTTP redirects, validates %PDF- binary magic bytes, computes SHA-256 checksums, and detects duplicate files.
- **PyMuPDF Text & Page-Aware Extraction**: Automatically segments manuscripts into structured page units and RAG semantic chunks (800 chars with 150-char overlap).
- **Scanned Document Detection**: Distinguishes between native vector text and scanned image PDFs, flagging documents for downstream OCR.
- **Polite Crawling**: Built-in configurable rate limiting, exponential backoff retries, and descriptive User-Agent.

### CLI Usage:

`powershell
# 1. Quick Dry-Run (Discovers repository collections and reports counts without downloading PDFs)
python -m crawler.cli --start-url http://14.139.119.23:8080/dspace/community-list --page-limit 25 --dry-run

# 2. Targeted Collection Ingestion (Download PDFs + Extract Text + Chunk for RAG)
python -m crawler.cli --start-url http://14.139.119.23:8080/dspace/handle/123456789/123 --page-limit 10 --download-mode all

# 3. Clean Re-crawl (Purges previous state database and starts fresh)
python -m crawler.cli --start-url http://14.139.119.23:8080/dspace/handle/123456789/133 --reset-state
`

### Generated Artifacts (data/):
`	ext
data/
  raw/
    pdfs/
      [expedition]/[document_id]_[safe_title].pdf
  metadata/
    documents.json           # Complete array of structured repository item metadata
    documents.csv            # Tabular metadata spreadsheet
    crawl_manifest.json      # Comprehensive audit manifest with execution timestamps & counts
    failed_downloads.json    # Detailed log of any restricted or failed bitstream downloads
  extracted/
    [document_id].txt        # Full plain text extraction
    [document_id].json       # Structured per-page text & scan quality scores
  chunks/
    document_chunks.jsonl    # Ready-to-index JSONL chunks with full provenance for RAG
  logs/
    crawler.log              # Real-time crawler logs
`

### Downstream Integration:
1. **Streamlit Assistant / ChromaDB**: Ingest document_chunks.jsonl directly into Chroma vector collection (
ag/vectorstore/chroma_store.py).
2. **React / Docusaurus Outreach Portal**: Import documents.json and document_chunks.jsonl to render publication catalogs, author index tables, and documentation pages.

## ⚖️ License & Provenance
Developed for the **Smart India Hackathon (SIH) 2024 / MoES Challenge 26063**.  
Data and publication bitstreams sourced from the **National Centre for Polar and Ocean Research (NCPOR)** and the **National Polar Data Center (NPDC)** under Government of India open scientific data policies.
