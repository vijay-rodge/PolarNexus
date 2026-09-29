import sys
import argparse
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from crawler.config import CrawlerConfig
from crawler.engine import CrawlerEngine

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(
        description="NCPOR DSpace Polar Science Knowledge Crawler & Ingestion Pipeline"
    )
    parser.add_argument(
        "--start-url",
        type=str,
        default="http://14.139.119.23:8080/dspace/community-list",
        help="Starting URL for repository discovery (default: community-list)"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum link traversal depth (default: 5)"
    )
    parser.add_argument(
        "--page-limit",
        type=int,
        default=25,
        help="Maximum pages to crawl in this execution batch (default: 25)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Politeness delay between HTTP requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--download-mode",
        type=str,
        choices=["all", "dry-run", "metadata-only"],
        default="all",
        help="Ingestion mode: 'all' (metadata + PDF + RAG chunks), 'dry-run' (discovery only), 'metadata-only' (no PDFs)"
    )
    parser.add_argument(
        "--traversal-mode",
        type=str,
        choices=["depth-first", "breadth-first"],
        default="depth-first",
        help="Queue traversal strategy: 'depth-first' (dives into collection items immediately) or 'breadth-first'"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Optional search intent / keyword filter (e.g. 'oceanographic', 'position fixing', 'meteorology')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Shortcut to run in discovery-only mode without downloading binary PDFs"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Output root directory for crawled artifacts (default: data)"
    )
    parser.add_argument(
        "--reset-state",
        action="store_true",
        help="Purges the crawler SQLite database before starting"
    )

    args = parser.parse_args()
    config = CrawlerConfig.from_args(args)

    if config.reset_state and config.db_path.exists():
        print(f"Purging existing crawler state at {config.db_path}...")
        config.db_path.unlink()

    if config.query and ("community-list" in config.start_url or "simple-search" in config.start_url):
        from crawler.dspace_search_harvester import DSpaceSearchHarvester
        print(f"\nTargeting live DSpace Search Harvester for query: '{config.query}'...")
        harvester = DSpaceSearchHarvester(config)
        res = harvester.search_and_harvest(config.query, max_items=config.page_limit, download_pdfs=(config.download_mode == "all"))

        print("\n" + "=" * 70)
        print("NCPOR DSPACE SEARCH & HARVEST SUMMARY REPORT")
        print("=" * 70)
        print(f"Query:                    '{res['query']}'")
        print(f"Total DSpace Hits:        {res['total_hits']}")
        print(f"Items Documented:         {len(res['harvested_items'])}")
        print(f"PDFs Downloaded:          {len([i for i in res['harvested_items'] if i.get('download_status') == 'downloaded'])}")
        print(f"RAG Chunks Generated:     {res['total_chunks_saved']}")
        print(f"Coordinates Extracted:    {len(res['coordinates'])}")
        print(f"Figures Extracted:        {len(res['extracted_figures'])}")
        print("=" * 70)
        # Safe print for Windows consoles
        safe_synthesis = res["natural_language_synthesis"].encode("ascii", errors="replace").decode("ascii")
        print("\n" + safe_synthesis)
        print("=" * 70 + "\n")
        return

    engine = CrawlerEngine(config)
    manifest = engine.run()

    summary = manifest.get("summary", {})
    print("\n" + "=" * 70)
    print("NCPOR CRAWLER SUMMARY REPORT")
    print("=" * 70)
    print(f"Pages Visited:            {summary.get('total_urls_visited', 0)}")
    print(f"URLs Discovered:          {summary.get('total_urls_discovered', 0)}")
    print(f"Items Documented:         {summary.get('total_items_discovered', 0)}")
    print(f"PDFs Downloaded:          {summary.get('total_pdfs_downloaded', 0)}")
    print(f"Text Chunks Extracted:    {summary.get('total_text_extracted', 0)}")
    print(f"Failed Downloads:         {summary.get('total_failed_downloads', 0)}")
    print(f"Restricted Documents:     {summary.get('total_restricted_documents', 0)}")
    print("=" * 70)
    print(f"Manifest written to:      {manifest['artifacts']['documents_json']}")
    print(f"RAG Chunks written to:    {manifest['artifacts']['chunks_file']}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
