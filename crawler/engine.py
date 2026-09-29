import time
import logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, Any, Optional

from crawler.config import CrawlerConfig
from crawler.state import CrawlerStateManager
from crawler.dspace_parser import DSpaceParser
from crawler.downloader import PDFDownloader
from crawler.extractor import PDFTextExtractor
from crawler.exporter import CrawlerExporter

logger = logging.getLogger("PolarScienceCrawler")

class CrawlerEngine:
    """
    Breadth-First Search (BFS) / Depth-First Priority crawler engine for NCPOR DSpace.
    Prioritizes diving into item pages to download PDFs and extract RAG chunks immediately.
    """

    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.config.ensure_directories()
        self._setup_logging()

        self.state = CrawlerStateManager(self.config.db_path)
        self.downloader = PDFDownloader(
            user_agent=self.config.user_agent,
            timeout=self.config.timeout,
            delay=self.config.request_delay,
            max_retries=self.config.max_retries
        )
        self.extractor = PDFTextExtractor()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.config.user_agent})

    def _setup_logging(self):
        log_file = self.config.logs_dir / "crawler.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(str(log_file), encoding="utf-8"),
                logging.StreamHandler()
            ]
        )

    def run(self) -> Dict[str, Any]:
        logger.info("=" * 70)
        logger.info("STARTING NCPOR DSPACE CRAWLER PIPELINE")
        logger.info(f"Target: {self.config.start_url}")
        logger.info(f"Mode: {self.config.download_mode.upper()} | Traversal: {self.config.traversal_mode.upper()} | Page Limit: {self.config.page_limit}")
        if self.config.query:
            logger.info(f"Intent Filter Query: '{self.config.query}'")
        logger.info("=" * 70)

        canon_start = DSpaceParser.canonicalize_url(self.config.start_url)
        self.state.add_url(self.config.start_url, canon_start, depth=0, url_type="community_list", priority=10)

        visited_count = 0

        while visited_count < self.config.page_limit:
            # Query queued URLs with configured traversal mode
            batch = self.state.get_queued_urls(limit=10, mode=self.config.traversal_mode)
            if not batch:
                logger.info("Queue empty. Traversal complete.")
                break

            for url, depth, predicted_type in batch:
                if visited_count >= self.config.page_limit:
                    logger.info(f"Reached configured page limit ({self.config.page_limit}). Stopping discovery.")
                    break

                if depth > self.config.max_depth:
                    self.state.mark_url_skipped(url, reason=f"Exceeded max depth {self.config.max_depth}")
                    continue

                logger.info(f"[{visited_count + 1}/{self.config.page_limit}] Crawling (Depth {depth}): {url}")
                time.sleep(self.config.request_delay)

                try:
                    resp = self.session.get(url, timeout=self.config.timeout, allow_redirects=True)
                    final_url = resp.url
                    http_code = resp.status_code

                    if http_code != 200:
                        logger.warning(f"HTTP {http_code} returned for {url}")
                        self.state.mark_url_visited(url, http_status=http_code, error_msg=f"HTTP status {http_code}")
                        visited_count += 1
                        continue

                    html_text = resp.text
                    soup = BeautifulSoup(html_text, 'html.parser')

                    # 1. Process Item Record (where metadata table & View/Open PDF table exist)
                    if DSpaceParser.is_item_page(soup, final_url):
                        item = DSpaceParser.parse_item_page(html_text, final_url)
                        if item:
                            # Apply optional intent filter if specified
                            if self.config.query:
                                q_lower = self.config.query.lower()
                                text_pool = f"{item.get('title', '')} {' '.join(item.get('keywords', []))} {item.get('collection', '')}".lower()
                                if q_lower not in text_pool:
                                    logger.info(f"  - Skipping Item (Does not match query '{self.config.query}'): '{item['title']}'")
                                    self.state.mark_url_visited(url, http_status=200)
                                    visited_count += 1
                                    continue

                            logger.info(f"  -> Discovered Item: '{item['title']}' ({item['item_id']})")
                            self.state.save_item(item)

                            if self.config.download_mode == "all" and item.get("primary_pdf_url"):
                                self._process_pdf_download(item)

                    # 2. Extract Outlinks for Graph Traversal
                    outlinks = DSpaceParser.extract_links(html_text, final_url, self.config.allowed_domains)
                    for out_url, ltype in outlinks:
                        if ltype == "bitstream":
                            continue

                        # Prioritize item/handle URLs so depth-first pops them immediately
                        canon = DSpaceParser.canonicalize_url(out_url)
                        link_priority = 5 if '/handle/' in out_url else 1
                        self.state.add_url(out_url, canon, depth=depth + 1, url_type=ltype, priority=link_priority)

                    self.state.mark_url_visited(url, http_status=200)
                    visited_count += 1

                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    self.state.mark_url_visited(url, http_status=0, error_msg=str(e))
                    visited_count += 1

        logger.info("Generating crawl manifests, structured JSON, CSV, and RAG chunks...")
        manifest = CrawlerExporter.export(
            state_manager=self.state,
            metadata_dir=self.config.metadata_dir,
            config=self.config
        )

        logger.info("=" * 70)
        logger.info("CRAWL EXECUTION COMPLETE")
        logger.info(f"Summary: {manifest['summary']}")
        logger.info("=" * 70)

        return manifest

    def _process_pdf_download(self, item: Dict[str, Any]):
        pdf_url = item["primary_pdf_url"]
        item_id = item["item_id"]
        title = item.get("title", "")
        expedition = item.get("expedition", "")

        logger.info(f"  -> Downloading PDF: {pdf_url}")
        dl_res = self.downloader.download_pdf(
            pdf_url=pdf_url,
            dest_dir=self.config.raw_pdf_dir,
            item_id=item_id,
            title=title,
            expedition=expedition
        )

        if dl_res["success"]:
            logger.info(f"  ✓ PDF Verified ({dl_res['file_size']:,} bytes, sha256: {dl_res['sha256'][:10]}...)")
            self.state.update_item_download(
                item_id=item_id,
                download_status="downloaded",
                file_path=dl_res["file_path"],
                sha256=dl_res["sha256"],
                file_size=dl_res["file_size"]
            )

            chunks_file = self.config.chunks_dir / "document_chunks.jsonl"
            ext_res = self.extractor.extract_and_chunk(
                pdf_path=dl_res["file_path"],
                item_metadata=item,
                extracted_dir=self.config.extracted_dir,
                chunks_file=chunks_file
            )

            # Record coordinates and figures in state
            coords = ext_res.get("coordinates", [])
            figures = ext_res.get("figures", [])
            self.state.update_item_extraction(
                item_id=item_id,
                extraction_status=ext_res["status"],
                coordinates=coords,
                figures=figures
            )

            logger.info(f"  ✓ Text Extracted: {ext_res['total_chars']} chars across {ext_res['total_pages']} pages -> {ext_res['chunks_count']} RAG chunks.")
            if coords:
                logger.info(f"  ✓ Geodetic Benchmarks Found: {len(coords)} coordinates parsed.")
            if figures:
                logger.info(f"  ✓ Figures Extracted: {len(figures)} images isolated.")

        else:
            status = "restricted" if dl_res["is_restricted"] else "failed"
            logger.warning(f"  ✗ PDF Download Failed: {dl_res['error']}")
            self.state.update_item_download(
                item_id=item_id,
                download_status=status,
                file_path="",
                sha256="",
                file_size=0,
                error_msg=dl_res["error"]
            )
            self.state.record_failed_download(
                url=pdf_url,
                item_id=item_id,
                error_type=status,
                error_detail=dl_res["error"] or "Unknown error",
                http_status=dl_res["http_status"]
            )
