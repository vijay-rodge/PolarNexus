import sqlite3
import json
import datetime
from datetime import timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

class CrawlerStateManager:
    """
    Manages persistent crawler state in SQLite to guarantee resume capability,
    depth-first priority routing, and auditable ingestion tracking.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self, reset: bool = False):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.get_connection() as conn:
            if reset:
                conn.execute("DROP TABLE IF EXISTS crawled_urls")
                conn.execute("DROP TABLE IF EXISTS discovered_items")
                conn.execute("DROP TABLE IF EXISTS failed_downloads")

            conn.execute("""
            CREATE TABLE IF NOT EXISTS crawled_urls (
                url TEXT PRIMARY KEY,
                canonical_url TEXT,
                url_type TEXT DEFAULT 'unknown',
                status TEXT DEFAULT 'queued',
                depth INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 0,
                http_status INTEGER DEFAULT 0,
                discovered_at TIMESTAMP,
                visited_at TIMESTAMP,
                error_msg TEXT
            )
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS discovered_items (
                item_id TEXT PRIMARY KEY,
                handle_url TEXT,
                title TEXT,
                authors TEXT,
                year INTEGER,
                collection TEXT,
                expedition TEXT,
                metadata_json TEXT,
                pdf_url TEXT,
                download_status TEXT DEFAULT 'pending',
                file_path TEXT,
                sha256 TEXT,
                file_size INTEGER DEFAULT 0,
                extracted_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS failed_downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                item_id TEXT,
                error_type TEXT,
                error_detail TEXT,
                http_status INTEGER DEFAULT 0,
                retry_count INTEGER DEFAULT 0,
                timestamp TIMESTAMP
            )
            """)
            conn.commit()

    def add_url(self, url: str, canonical_url: str, depth: int, url_type: str = "unknown", priority: int = 0) -> bool:
        now = datetime.datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            try:
                conn.execute(
                    "INSERT INTO crawled_urls (url, canonical_url, url_type, status, depth, priority, discovered_at) VALUES (?, ?, ?, 'queued', ?, ?, ?)",
                    (url, canonical_url, url_type, depth, priority, now)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def is_url_visited(self, url: str) -> bool:
        with self.get_connection() as conn:
            cur = conn.execute("SELECT status FROM crawled_urls WHERE url = ?", (url,))
            row = cur.fetchone()
            return row is not None and row["status"] in ["visited", "failed", "skipped"]

    def get_queued_urls(self, limit: int = 10, mode: str = "depth-first") -> List[Tuple[str, int, str]]:
        with self.get_connection() as conn:
            if mode == "depth-first":
                # Depth-first prioritization: deeper item nodes crawl FIRST before sibling collections
                query = """
                SELECT url, depth, url_type FROM crawled_urls 
                WHERE status = 'queued' 
                ORDER BY 
                    priority DESC,
                    depth DESC, 
                    rowid DESC 
                LIMIT ?
                """
            else:
                # Breadth-first
                query = """
                SELECT url, depth, url_type FROM crawled_urls 
                WHERE status = 'queued' 
                ORDER BY 
                    depth ASC, 
                    rowid ASC 
                LIMIT ?
                """
            cur = conn.execute(query, (limit,))
            return [(r["url"], r["depth"], r["url_type"]) for r in cur.fetchall()]

    def mark_url_visited(self, url: str, http_status: int = 200, error_msg: Optional[str] = None):
        now = datetime.datetime.now(timezone.utc).isoformat()
        status = "failed" if error_msg else "visited"
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE crawled_urls SET status = ?, http_status = ?, visited_at = ?, error_msg = ? WHERE url = ?",
                (status, http_status, now, error_msg, url)
            )
            conn.commit()

    def mark_url_skipped(self, url: str, reason: str):
        now = datetime.datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE crawled_urls SET status = 'skipped', visited_at = ?, error_msg = ? WHERE url = ?",
                (now, reason, url)
            )
            conn.commit()

    def save_item(self, item: Dict[str, Any]):
        now = datetime.datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            meta_str = json.dumps(item, ensure_ascii=False)
            conn.execute("""
            INSERT INTO discovered_items (
                item_id, handle_url, title, authors, year, collection, expedition,
                metadata_json, pdf_url, download_status, file_path, sha256, file_size,
                extracted_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
                title = excluded.title,
                authors = excluded.authors,
                year = excluded.year,
                collection = excluded.collection,
                expedition = excluded.expedition,
                metadata_json = excluded.metadata_json,
                pdf_url = excluded.pdf_url,
                updated_at = excluded.updated_at
            """, (
                item["item_id"],
                item.get("handle_url", ""),
                item.get("title", ""),
                item.get("authors", ""),
                item.get("year"),
                item.get("collection", ""),
                item.get("expedition", ""),
                meta_str,
                item.get("primary_pdf_url") or item.get("pdf_url", ""),
                item.get("download_status", "pending"),
                item.get("file_path", ""),
                item.get("sha256", ""),
                item.get("file_size_bytes", 0),
                item.get("extraction_status", "pending"),
                now,
                now
            ))
            conn.commit()

    def update_item_download(self, item_id: str, download_status: str, file_path: str, sha256: str, file_size: int, error_msg: Optional[str] = None):
        now = datetime.datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            cur = conn.execute("SELECT metadata_json FROM discovered_items WHERE item_id = ?", (item_id,))
            row = cur.fetchone()
            meta_str = None
            if row:
                meta = json.loads(row["metadata_json"])
                meta["download_status"] = download_status
                meta["file_path"] = file_path
                meta["sha256"] = sha256
                meta["file_size_bytes"] = file_size
                if error_msg:
                    meta["download_error"] = error_msg
                meta_str = json.dumps(meta, ensure_ascii=False)
            conn.execute("""
            UPDATE discovered_items 
            SET download_status = ?, file_path = ?, sha256 = ?, file_size = ?, metadata_json = COALESCE(?, metadata_json), updated_at = ?
            WHERE item_id = ?
            """, (download_status, file_path, sha256, file_size, meta_str, now, item_id))
            conn.commit()

    def update_item_extraction(self, item_id: str, extraction_status: str, coordinates: Optional[list] = None, figures: Optional[list] = None):
        now = datetime.datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            cur = conn.execute("SELECT metadata_json FROM discovered_items WHERE item_id = ?", (item_id,))
            row = cur.fetchone()
            meta_str = None
            if row:
                meta = json.loads(row["metadata_json"])
                meta["extraction_status"] = extraction_status
                if coordinates is not None:
                    meta["coordinates"] = coordinates
                if figures is not None:
                    meta["extracted_figures"] = figures
                meta_str = json.dumps(meta, ensure_ascii=False)
            conn.execute("UPDATE discovered_items SET extracted_status = ?, metadata_json = COALESCE(?, metadata_json), updated_at = ? WHERE item_id = ?",
                         (extraction_status, meta_str, now, item_id))
            conn.commit()

    def record_failed_download(self, url: str, item_id: str, error_type: str, error_detail: str, http_status: int = 0):
        now = datetime.datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            conn.execute("""
            INSERT INTO failed_downloads (url, item_id, error_type, error_detail, http_status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (url, item_id, error_type, error_detail, http_status, now))
            conn.commit()

    def is_sha256_downloaded(self, sha256: str) -> Optional[str]:
        if not sha256:
            return None
        with self.get_connection() as conn:
            cur = conn.execute("SELECT file_path FROM discovered_items WHERE sha256 = ? AND download_status = 'downloaded'", (sha256,))
            row = cur.fetchone()
            return row["file_path"] if row else None

    def get_all_items(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.execute("SELECT metadata_json FROM discovered_items ORDER BY created_at ASC")
            return [json.loads(r["metadata_json"]) for r in cur.fetchall()]

    def get_summary(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            total_urls = conn.execute("SELECT COUNT(*) FROM crawled_urls").fetchone()[0]
            visited_urls = conn.execute("SELECT COUNT(*) FROM crawled_urls WHERE status = 'visited'").fetchone()[0]
            items_disc = conn.execute("SELECT COUNT(*) FROM discovered_items").fetchone()[0]
            downloaded = conn.execute("SELECT COUNT(*) FROM discovered_items WHERE download_status = 'downloaded'").fetchone()[0]
            failed_dl = conn.execute("SELECT COUNT(*) FROM discovered_items WHERE download_status = 'failed'").fetchone()[0]
            restricted = conn.execute("SELECT COUNT(*) FROM discovered_items WHERE download_status = 'restricted'").fetchone()[0]
            extracted = conn.execute("SELECT COUNT(*) FROM discovered_items WHERE extracted_status = 'completed'").fetchone()[0]
            ocr_needed = conn.execute("SELECT COUNT(*) FROM discovered_items WHERE extracted_status = 'ocr_required'").fetchone()[0]

            return {
                "total_urls_discovered": total_urls,
                "total_urls_visited": visited_urls,
                "total_items_discovered": items_disc,
                "total_pdfs_downloaded": downloaded,
                "total_failed_downloads": failed_dl,
                "total_restricted_documents": restricted,
                "total_text_extracted": extracted,
                "total_ocr_required": ocr_needed
            }
