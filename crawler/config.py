import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass
class CrawlerConfig:
    start_url: str = "http://14.139.119.23:8080/dspace/community-list"
    allowed_domains: List[str] = field(default_factory=lambda: ["14.139.119.23", "14.139.119.23:8080"])
    output_dir: str = "data"
    max_depth: int = 5
    page_limit: int = 25
    request_delay: float = 1.0
    download_mode: str = "all"  # 'all', 'dry-run', 'metadata-only'
    traversal_mode: str = "depth-first"  # 'depth-first' (dives into items), 'breadth-first'
    query: Optional[str] = None  # Optional keyword filter for targeted collection crawling
    user_agent: str = "PolarScienceCrawler/1.0 (NCPOR-SIH-Research-Bot; +http://ncpor.res.in)"
    timeout: int = 25
    max_retries: int = 3
    ocr_enabled: bool = True
    reset_state: bool = False

    @property
    def output_path(self) -> Path:
        return Path(self.output_dir)

    @property
    def raw_pdf_dir(self) -> Path:
        return self.output_path / "raw" / "pdfs"

    @property
    def metadata_dir(self) -> Path:
        return self.output_path / "metadata"

    @property
    def extracted_dir(self) -> Path:
        return self.output_path / "extracted"

    @property
    def chunks_dir(self) -> Path:
        return self.output_path / "chunks"

    @property
    def logs_dir(self) -> Path:
        return self.output_path / "logs"

    @property
    def db_path(self) -> Path:
        return self.output_path / "crawler_state.db"

    def ensure_directories(self):
        for p in [self.raw_pdf_dir, self.metadata_dir, self.extracted_dir, self.chunks_dir, self.logs_dir]:
            p.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "CrawlerConfig":
        return cls(
            start_url=args.start_url or "http://14.139.119.23:8080/dspace/community-list",
            output_dir=args.output_dir or "data",
            max_depth=args.max_depth,
            page_limit=args.page_limit,
            request_delay=args.delay,
            download_mode="dry-run" if args.dry_run else args.download_mode,
            traversal_mode=args.traversal_mode,
            query=args.query,
            reset_state=args.reset_state
        )
