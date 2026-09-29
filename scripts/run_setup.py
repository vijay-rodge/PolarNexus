import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

def run_setup():
    """Initializes the complete Polar Science knowledge platform."""
    print("=" * 60)
    print("Initializing NCPOR Polar Science Platform (SIH 26063)")
    print("=" * 60)

    # 1. Database Initialization & Seeding
    print("\n[1/3] Checking and seeding relational database...")
    from database.seed_data import seed_database
    seed_database()

    # 2. Synchronize DSpace Publications & Figures
    print("\n[2/3] Analyzing DSpace research manuscripts & extracting figures...")
    from scientific_engine.document_analyzer import ScientificDocumentAnalyzer
    pdf_p = root_dir / "data" / "raw" / "publications" / "123456789_133_File_Description_SizeFormat_ARTICLE_4.pdf"
    if pdf_p.exists():
        analysis = ScientificDocumentAnalyzer.synthesize_publication(str(pdf_p), "PUB-DSPACE-123456789-133")
        print(f"  Extracted {len(analysis['coordinates'])} geodetic coordinates.")
        print(f"  Extracted {len(analysis['figures'])} high-resolution figures.")
    else:
        print("  Notice: Sample publication PDF not found. Skipping document analysis.")

    # 3. Vector Store Check
    print("\n[3/3] Initializing ChromaDB vector store collection...")
    from rag.vectorstore.chroma_store import PolarVectorStore
    coll = PolarVectorStore.get_collection()
    print(f"  Chroma collection status: {type(coll)}")

    print("\n" + "=" * 60)
    print("Setup Complete! You can now run:")
    print("  streamlit run streamlit_app/app.py")
    print("=" * 60)

if __name__ == "__main__":
    run_setup()
