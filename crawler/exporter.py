import csv
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List

class CrawlerExporter:
    """
    Exports structured metadata, tabular CSVs, and comprehensive crawl manifests
    for integration into downstream portals, Docusaurus, and ChromaDB RAG.
    """

    @classmethod
    def export(cls, state_manager, metadata_dir: Path, config) -> Dict[str, Any]:
        metadata_dir.mkdir(parents=True, exist_ok=True)
        items = state_manager.get_all_items()
        summary = state_manager.get_summary()

        docs_json_path = metadata_dir / "documents.json"
        with open(docs_json_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

        docs_csv_path = metadata_dir / "documents.csv"
        csv_headers = [
            "item_id", "title", "authors", "year", "issue_date", "collection",
            "expedition", "series_report_no", "handle_url", "handle_uri",
            "pdf_url", "download_status", "file_path", "sha256", "file_size_bytes",
            "extraction_status"
        ]
        with open(docs_csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers, extrasaction="ignore")
            writer.writeheader()
            for item in items:
                row = {h: item.get(h, "") for h in csv_headers}
                row["pdf_url"] = item.get("primary_pdf_url", "")
                row["keywords"] = ", ".join(item.get("keywords", []))
                writer.writerow(row)

        failed_path = metadata_dir / "failed_downloads.json"
        failed_records = []
        with state_manager.get_connection() as conn:
            cur = conn.execute("SELECT * FROM failed_downloads ORDER BY timestamp DESC")
            for r in cur.fetchall():
                failed_records.append(dict(r))
        with open(failed_path, "w", encoding="utf-8") as f:
            json.dump(failed_records, f, indent=2)

        manifest_path = metadata_dir / "crawl_manifest.json"
        manifest = {
            "crawler_name": "NCPOR Polar Science DSpace Harvester",
            "crawler_version": "1.0.0",
            "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "start_url": config.start_url,
            "download_mode": config.download_mode,
            "max_depth": config.max_depth,
            "page_limit": config.page_limit,
            "summary": summary,
            "artifacts": {
                "documents_json": str(docs_json_path),
                "documents_csv": str(docs_csv_path),
                "failed_downloads_json": str(failed_path),
                "chunks_file": str(config.chunks_dir / "document_chunks.jsonl")
            }
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest
