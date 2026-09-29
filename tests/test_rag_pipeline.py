import pytest
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from rag.chunkers.semantic_chunker import SectionAwareChunker
from rag.cleaners.text_cleaner import DocumentCleaner
from rag.vectorstore.chroma_store import PolarVectorStore

def test_document_cleaner_strips_page_numbers():
    raw = "Page 12 of 85\n\nSECTION 1: INTRODUCTION\n\nSome scientific text.\n\n42\n\nMore text."
    cleaned = DocumentCleaner.clean(raw)
    assert "Page 12 of 85" not in cleaned
    assert "SECTION 1: INTRODUCTION" in cleaned
    assert "Some scientific text." in cleaned

def test_section_aware_chunker_metadata():
    doc_text = """SECTION 1: RESEARCH IN SVALBARD
The Arctic expedition established fjord monitoring stations.

SECTION 2: GLACIOLOGY SURVEYS
Ground penetrating radar measured ice shelf thickness.
"""
    chunks = SectionAwareChunker.chunk_document(
        text=doc_text,
        document_id="DOC-TEST-001",
        source_name="NCPOR Test",
        source_url="https://ncpor.res.in/test.pdf",
        default_station="Himadri"
    )

    assert len(chunks) >= 2
    for c in chunks:
        assert "chunk_id" in c
        assert c["document_id"] == "DOC-TEST-001"
        assert c["station"] == "Himadri"
        assert "section" in c
        assert c["page"] >= 1

def test_vectorstore_similarity_retrieval():
    results = PolarVectorStore.similarity_search("Maitri meteorological observatory", top_k=3)
    assert len(results) > 0
    top_doc = results[0]
    assert "content" in top_doc
    assert "metadata" in top_doc
    assert "relevance_score" in top_doc
