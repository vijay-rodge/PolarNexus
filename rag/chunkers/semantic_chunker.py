import re
import uuid
from typing import List, Dict, Any
from rag.cleaners.text_cleaner import DocumentCleaner

class SectionAwareChunker:
    @classmethod
    def chunk_document(
        cls,
        text: str,
        document_id: str,
        source_name: str,
        source_url: str,
        default_station: str = "All",
        default_expedition: str = "General",
        default_research_area: str = "Polar Science",
        max_chunk_size: int = 800,
        chunk_overlap: int = 100
    ) -> List[Dict[str, Any]]:
        cleaned_text = DocumentCleaner.clean(text)
        section_pattern = r'(SECTION\s+\d+:?[^\n]+|CHAPTER\s+\d+:?[^\n]+|[A-Z\s]{4,}:)'
        splits = re.split(section_pattern, cleaned_text)
        
        chunks = []
        current_section = "General Overview"
        current_page = 1

        if len(splits) <= 1:
            sections_data = [(current_section, cleaned_text)]
        else:
            sections_data = []
            for i in range(1, len(splits), 2):
                sec_header = splits[i].strip()
                sec_body = splits[i+1].strip() if i+1 < len(splits) else ""
                sections_data.append((sec_header, sec_body))

        for sec_header, sec_body in sections_data:
            current_section = sec_header
            paragraphs = sec_body.split('\n\n')
            current_chunk_text = ""

            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue

                if len(current_chunk_text) + len(p) <= max_chunk_size:
                    current_chunk_text += ("\n\n" if current_chunk_text else "") + p
                else:
                    if current_chunk_text:
                        chunk_id = f"CHK-{uuid.uuid4().hex[:8].upper()}"
                        chunks.append({
                            "chunk_id": chunk_id,
                            "document_id": document_id,
                            "source_name": source_name,
                            "source_url": source_url,
                            "page": current_page,
                            "section": current_section,
                            "expedition": default_expedition,
                            "station": default_station,
                            "research_area": default_research_area,
                            "content": current_chunk_text.strip()
                        })
                        current_page += 1
                    current_chunk_text = p

            if current_chunk_text:
                chunk_id = f"CHK-{uuid.uuid4().hex[:8].upper()}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "source_name": source_name,
                    "source_url": source_url,
                    "page": current_page,
                    "section": current_section,
                    "expedition": default_expedition,
                    "station": default_station,
                    "research_area": default_research_area,
                    "content": current_chunk_text.strip()
                })
                current_page += 1

        return chunks
