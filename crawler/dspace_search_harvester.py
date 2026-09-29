import urllib.parse
import requests
import bs4
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from crawler.config import CrawlerConfig
from crawler.dspace_parser import DSpaceParser
from crawler.downloader import PDFDownloader
from crawler.extractor import PDFTextExtractor
from scientific_engine.document_analyzer import DocumentAnalyzer
from rag.vectorstore.chroma_store import PolarVectorStore

logger = logging.getLogger("DSpaceSearchHarvester")

class DSpaceSearchHarvester:
    """
    Automated DSpace Search and Live Harvester:
    1. Queries DSpace simple-search for keywords (e.g. 'oceanology').
    2. Scrapes item hyperlinks from search hits (e.g. handles 281, 754).
    3. Scrapes item metadata and PDF bitstream links from 'Files in This Item' table.
    4. Downloads permitted PDFs, validates binary magic bytes and checksums.
    5. Extracts text page-by-page, generates RAG chunks, and saves to document_chunks.jsonl.
    6. Extracts geodetic coordinates for interactive maps and isolates figures/diagrams.
    7. Synthesizes a structured natural language scientific response.
    8. Upserts chunks into Chroma vector store for immediate assistant queries.
    """

    def __init__(self, config: Optional[CrawlerConfig] = None):
        self.config = config or CrawlerConfig()
        self.config.ensure_directories()
        self.downloader = PDFDownloader(
            user_agent=self.config.user_agent,
            timeout=self.config.timeout,
            delay=self.config.request_delay,
            max_retries=self.config.max_retries
        )
        self.extractor = PDFTextExtractor()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.config.user_agent})

    def search_and_harvest(
        self,
        query: str,
        max_items: int = 5,
        download_pdfs: bool = True
    ) -> Dict[str, Any]:
        clean_query = query.strip()
        search_url = f"http://14.139.119.23:8080/dspace/simple-search?query={urllib.parse.quote_plus(clean_query)}"
        logger.info(f"Querying DSpace search: {search_url}")

        hits = []
        try:
            resp = self.session.get(search_url, timeout=self.config.timeout)
            if resp.status_code == 200:
                soup = bs4.BeautifulSoup(resp.text, "html.parser")
                seen_handles = set()
                for tr in soup.find_all("tr"):
                    links = tr.find_all("a", href=True)
                    for a in links:
                        href = a["href"]
                        if "/handle/" in href and a.get_text(strip=True):
                            full_url = DSpaceParser.canonicalize_url(href, search_url)
                            if full_url not in seen_handles:
                                seen_handles.add(full_url)
                                hits.append({
                                    "title": a.get_text(strip=True),
                                    "url": full_url
                                })
        except Exception as e:
            logger.error(f"Failed to query DSpace search endpoint: {e}")

        hits = hits[:max_items]

        harvested_items: List[Dict[str, Any]] = []
        all_coordinates: List[Dict[str, Any]] = []
        all_figures: List[Dict[str, Any]] = []
        total_chunks_saved = 0

        chunks_file = self.config.chunks_dir / "document_chunks.jsonl"

        for hit in hits:
            item_url = hit["url"]
            logger.info(f"Scraping DSpace item record: {item_url}")
            try:
                item_resp = self.session.get(item_url, timeout=self.config.timeout)
                if item_resp.status_code != 200:
                    continue

                item_meta = DSpaceParser.parse_item_page(item_resp.text, item_url)
                if not item_meta:
                    continue

                item_meta["search_query"] = clean_query
                item_meta["download_status"] = "pending"
                item_meta["extraction_status"] = "pending"
                item_meta["coordinates"] = []
                item_meta["extracted_figures"] = []

                if download_pdfs and item_meta.get("primary_pdf_url"):
                    pdf_url = item_meta["primary_pdf_url"]
                    dl_res = self.downloader.download_pdf(
                        pdf_url=pdf_url,
                        dest_dir=self.config.raw_pdf_dir,
                        item_id=item_meta["item_id"],
                        title=item_meta.get("title", ""),
                        expedition=item_meta.get("expedition", "")
                    )

                    if dl_res["success"]:
                        item_meta["download_status"] = "downloaded"
                        item_meta["local_pdf_path"] = dl_res["file_path"]
                        item_meta["file_size_bytes"] = dl_res["file_size"]
                        item_meta["sha256"] = dl_res["sha256"]

                        ext_res = self.extractor.extract_and_chunk(
                            pdf_path=dl_res["file_path"],
                            item_metadata=item_meta,
                            extracted_dir=self.config.extracted_dir,
                            chunks_file=chunks_file
                        )

                        item_coords = ext_res.get("coordinates", [])
                        item_figs = ext_res.get("figures", [])
                        item_meta["coordinates"] = item_coords
                        item_meta["extracted_figures"] = item_figs
                        item_meta["extraction_status"] = ext_res["status"]
                        item_meta["total_pages"] = ext_res.get("total_pages", 0)
                        item_meta["total_characters"] = ext_res.get("total_chars", 0)
                        item_meta["chunks_count"] = ext_res.get("chunks_count", 0)

                        all_coordinates.extend(item_coords)
                        all_figures.extend(item_figs)
                        total_chunks_saved += ext_res.get("chunks_count", 0)

                        txt_path = self.config.extracted_dir / f"{item_meta['item_id']}.txt"
                        if txt_path.exists():
                            item_meta["extracted_text"] = txt_path.read_text(encoding="utf-8", errors="ignore")

                harvested_items.append(item_meta)

            except Exception as e:
                logger.error(f"Error harvesting item {item_url}: {e}")

        self._update_documents_metadata(harvested_items)

        try:
            new_chunks = self._load_recent_chunks(harvested_items)
            if new_chunks:
                PolarVectorStore.index_chunks(new_chunks)
                logger.info(f"Indexed {len(new_chunks)} chunks into Chroma vector store.")
        except Exception as e:
            logger.warning(f"Could not index chunks into vector store: {e}")

        deduped_coords = self._deduplicate_coords(all_coordinates)
        deduped_figs = self._deduplicate_figures(all_figures)

        synthesis = self._synthesize_natural_language_response(clean_query, harvested_items, deduped_coords, deduped_figs)

        return {
            "query": clean_query,
            "search_url": search_url,
            "total_hits": len(hits),
            "harvested_items": harvested_items,
            "coordinates": deduped_coords,
            "extracted_figures": deduped_figs,
            "total_chunks_saved": total_chunks_saved,
            "natural_language_synthesis": synthesis
        }

    def _update_documents_metadata(self, new_items: List[Dict[str, Any]]):
        docs_file = self.config.metadata_dir / "documents.json"
        existing_items = []
        if docs_file.exists():
            try:
                with open(docs_file, "r", encoding="utf-8") as f:
                    existing_items = json.load(f)
            except Exception:
                existing_items = []

        item_map = {it.get("item_id"): it for it in existing_items if it.get("item_id")}
        for it in new_items:
            clean_it = {k: v for k, v in it.items() if k != "extracted_text"}
            item_map[clean_it.get("item_id")] = clean_it

        all_docs = list(item_map.values())
        with open(docs_file, "w", encoding="utf-8") as f:
            json.dump(all_docs, f, indent=2)

    def _load_recent_chunks(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks_file = self.config.chunks_dir / "document_chunks.jsonl"
        if not chunks_file.exists():
            return []

        item_ids = {it.get("item_id"): True for it in items if it.get("item_id")}
        matched_chunks = []
        with open(chunks_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    c = json.loads(line)
                    if c.get("document_id") in item_ids:
                        if "content" not in c and "text" in c:
                            c["content"] = c["text"]
                        if "source_name" not in c and "title" in c:
                            c["source_name"] = c.get("title", "NCPOR Publication")
                        matched_chunks.append(c)
                except Exception:
                    continue
        return matched_chunks

    def _deduplicate_coords(self, coords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        deduped = []
        for c in coords:
            key = (round(float(c.get("latitude", 0)), 4), round(float(c.get("longitude", 0)), 4))
            if key not in seen:
                seen.add(key)
                deduped.append(c)
        return deduped

    def _deduplicate_figures(self, figures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        deduped = []
        for f in figures:
            p = f.get("file_path", "")
            if p and p not in seen:
                seen.add(p)
                deduped.append(f)
        return deduped

    def _synthesize_natural_language_response(
        self,
        query: str,
        items: List[Dict[str, Any]],
        coords: List[Dict[str, Any]],
        figs: List[Dict[str, Any]]
    ) -> str:
        if not items:
            return f"No documents found in the NCPOR DSpace repository matching '{query}'."

        combined_text = "\n\n".join([it.get("extracted_text", "") for it in items if it.get("extracted_text")])
        primary_title = items[0].get("title", f"Scientific Query: {query}")

        summary = DocumentAnalyzer.generate_executive_summary(
            text=combined_text or primary_title,
            title=f"Scientific Analysis: {query.title()} Research in Antarctica"
        )

        lines = [
            summary,
            "",
            "#### 5. Harvested Repository Manuscripts & Provenance",
        ]
        for idx, it in enumerate(items, 1):
            lines.append(
                f"{idx}. **{it.get('title')}**\n"
                f"   - **Author(s)**: {it.get('authors', 'N/A')} | **Date**: {it.get('issue_date', 'N/A')}\n"
                f"   - **Collection**: {it.get('collection', 'N/A')} | **DSpace Identifier**: `{it.get('item_id')}`\n"
                f"   - **Repository Handle**: [{it.get('handle_url')}]({it.get('handle_url')})\n"
                f"   - **Original Bitstream PDF**: [{it.get('primary_pdf_url')}]({it.get('primary_pdf_url')})"
            )

        if coords:
            lines.extend([
                "",
                f"#### 6. Geospatial Coordinates & Survey Benchmarks ({len(coords)} Plotted Locations)",
                "The scientific manuscripts contain verified navigational and geodetic reference points, plotted on the interactive map below:"
            ])
            for c in coords[:6]:
                lines.append(f"- **{c.get('name', 'Survey Benchmark')}**: `{c.get('dms_lat', '')}, {c.get('dms_lon', '')}` (Lat: `{c.get('latitude')}`, Lon: `{c.get('longitude')}`)")

        if figs:
            lines.extend([
                "",
                f"#### 7. Extracted Scientific Media & Diagrams ({len(figs)} Visual Assets)",
                "High-resolution figures, sea-ice charts, and satellite orbit trajectories extracted directly from the manuscript bitstreams:"
            ])
            for f in figs[:5]:
                lines.append(f"- 🖼️ **{f.get('caption', 'Scientific Figure')}** (Page {f.get('page', 1)})")

        return "\n".join(lines)
