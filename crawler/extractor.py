import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from scientific_engine.document_analyzer import DocumentAnalyzer

class PDFTextExtractor:
    """
    High-fidelity PDF text extraction, scanned-document detection, 
    geodetic coordinate parsing, figure extraction, and RAG chunk generation.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_and_chunk(
        self,
        pdf_path: str,
        item_metadata: Dict[str, Any],
        extracted_dir: Path,
        chunks_file: Path
    ) -> Dict[str, Any]:
        p_path = Path(pdf_path)
        if not p_path.exists():
            return {"status": "failed", "error": f"File not found: {pdf_path}", "chunks_count": 0, "coordinates": [], "figures": []}

        item_id = item_metadata.get("item_id", p_path.stem)
        title = item_metadata.get("title", "")
        authors = item_metadata.get("authors", "")
        year = item_metadata.get("year")
        expedition = item_metadata.get("expedition", "")
        collection = item_metadata.get("collection", "")
        source_url = item_metadata.get("handle_url", "")

        pages_data: List[Dict[str, Any]] = []
        total_chars = 0
        total_pages = 0

        try:
            import fitz
            doc = fitz.open(str(p_path))
            total_pages = len(doc)

            for page_idx, page in enumerate(doc, start=1):
                page_text = page.get_text("text") or ""
                cleaned_text = re.sub(r'[ \t]+', ' ', page_text)
                cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()

                char_count = len(cleaned_text)
                total_chars += char_count

                pages_data.append({
                    "page_number": page_idx,
                    "text": cleaned_text,
                    "char_count": char_count
                })

            doc.close()

        except Exception as e:
            return {"status": "failed", "error": f"PyMuPDF extraction error: {e}", "chunks_count": 0, "coordinates": [], "figures": []}

        avg_chars_per_page = total_chars / max(total_pages, 1)
        is_scanned = total_chars < 150 or avg_chars_per_page < 30
        extraction_status = "ocr_required" if is_scanned else "completed"

        full_text = "\n\n--- Page Break ---\n\n".join(
            f"=== Page {p['page_number']} ===\n{p['text']}" for p in pages_data if p['text']
        )

        # 1. Automatic Geodetic Coordinates Extraction
        coordinates = DocumentAnalyzer.extract_geodetic_coordinates(full_text)

        # 2. Automatic Figure and Diagram Extraction
        fig_output_dir = extracted_dir.parent / "media" / "extracted_figures"
        figures = DocumentAnalyzer.extract_figures(str(p_path), output_dir=str(fig_output_dir))

        # 3. Generate RAG semantic chunks
        chunks = self._generate_chunks(
            pages_data=pages_data,
            item_id=item_id,
            title=title,
            authors=authors,
            year=year,
            expedition=expedition,
            collection=collection,
            source_url=source_url
        )

        # Write text and structured JSON to extracted/
        txt_out = extracted_dir / f"{item_id}.txt"
        with open(txt_out, "w", encoding="utf-8") as f:
            f.write(full_text)

        json_out = extracted_dir / f"{item_id}.json"
        doc_record = {
            "item_id": item_id,
            "title": title,
            "authors": authors,
            "year": year,
            "expedition": expedition,
            "collection": collection,
            "source_url": source_url,
            "total_pages": total_pages,
            "total_characters": total_chars,
            "is_scanned": is_scanned,
            "extraction_status": extraction_status,
            "coordinates": coordinates,
            "figures": figures,
            "pages": pages_data
        }
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(doc_record, f, indent=2, ensure_ascii=False)

        # Append chunks to document_chunks.jsonl (avoid duplicate chunks)
        if chunks:
            existing_chunk_ids = set()
            if chunks_file.exists():
                with open(chunks_file, "r", encoding="utf-8") as f_in:
                    for line in f_in:
                        if line.strip():
                            try:
                                ch_obj = json.loads(line)
                                existing_chunk_ids.add(ch_obj.get("chunk_id"))
                            except Exception:
                                pass

            with open(chunks_file, "a", encoding="utf-8") as f:
                for ch in chunks:
                    if ch["chunk_id"] not in existing_chunk_ids:
                        f.write(json.dumps(ch, ensure_ascii=False) + "\n")
                        existing_chunk_ids.add(ch["chunk_id"])

        return {
            "status": extraction_status,
            "is_scanned": is_scanned,
            "total_pages": total_pages,
            "total_chars": total_chars,
            "chunks_count": len(chunks),
            "coordinates_count": len(coordinates),
            "figures_count": len(figures),
            "coordinates": coordinates,
            "figures": figures,
            "txt_path": str(txt_out),
            "json_path": str(json_out)
        }

    def _generate_chunks(
        self,
        pages_data: List[Dict[str, Any]],
        item_id: str,
        title: str,
        authors: str,
        year: Optional[int],
        expedition: str,
        collection: str,
        source_url: str
    ) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []

        for p in pages_data:
            text = p["text"]
            pg_num = p["page_number"]
            if len(text) < 40:
                continue

            start = 0
            chunk_idx = 1
            while start < len(text):
                end = start + self.chunk_size
                chunk_str = text[start:end].strip()

                if len(chunk_str) >= 40:
                    chunks.append({
                        "chunk_id": f"{item_id}_p{pg_num}_c{chunk_idx}",
                        "document_id": item_id,
                        "title": title,
                        "authors": authors,
                        "year": year,
                        "expedition": expedition,
                        "collection": collection,
                        "page_number": pg_num,
                        "text": chunk_str,
                        "source_url": source_url
                    })
                    chunk_idx += 1

                start += (self.chunk_size - self.chunk_overlap)

        return chunks
