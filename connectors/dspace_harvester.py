import os
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from connectors.base import BaseHarvester

class DSpaceHarvester(BaseHarvester):
    """
    Harvester for NCPOR DSpace Institutional Repository (http://14.139.119.23:8080/dspace/).
    Navigates communities, collections, search queries, extracts Dublin Core metadata,
    and downloads digital PDF bitstreams for scientific ingestion.
    """
    DEFAULT_BASE_URL = "http://14.139.119.23:8080/dspace"

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "NCPOR-PolarSciencePortal-Harvester/1.0 (MoES SIH-26063)"
        })

    def get_handle_url(self, handle: str) -> str:
        """Constructs full handle URL from handle string (e.g. '123456789/133')."""
        clean_handle = handle.replace("http://hdl.handle.net/", "").replace(self.base_url, "").strip("/")
        if not clean_handle.startswith("handle/"):
            clean_handle = f"handle/{clean_handle}"
        return f"{self.base_url}/{clean_handle}"

    def harvest_item_metadata(self, handle_or_url: str) -> Dict[str, Any]:
        """
        Parses item page (e.g. handle/123456789/133) and extracts:
        - Title, Authors, Issue Date, Abstract, Keywords, Series/Report No, Bitstream PDF links.
        """
        if handle_or_url.startswith("http"):
            url = handle_or_url
        else:
            url = self.get_handle_url(handle_or_url)

        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            return {"error": f"Failed to connect to DSpace server: {e}", "url": url}

        soup = BeautifulSoup(html, "html.parser")
        metadata = {
            "source_url": url,
            "title": "",
            "authors": "",
            "issue_date": "",
            "publisher": "NCPOR",
            "citation": "",
            "series_no": "",
            "abstract": "",
            "pdf_links": []
        }

        # Parse standard item display table
        tables = soup.find_all("table", class_="itemDisplayTable")
        if not tables:
            tables = soup.find_all("table")

        for table in tables:
            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    val = cells[1].get_text(strip=True)

                    if "title" in label:
                        metadata["title"] = val
                    elif "author" in label:
                        metadata["authors"] = val
                    elif "date" in label or "issue" in label:
                        metadata["issue_date"] = val
                    elif "series" in label or "report" in label:
                        metadata["series_no"] = val
                    elif "abstract" in label or "description" in label:
                        metadata["abstract"] = val

        # Extract PDF bitstreams from file links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "bitstream" in href.lower() or href.lower().endswith(".pdf"):
                full_pdf_url = urllib.parse.urljoin(self.base_url, href)
                metadata["pdf_links"].append({
                    "name": a.get_text(strip=True) or Path(href).name,
                    "url": full_pdf_url
                })

        return metadata

    def download_pdf(self, pdf_url: str, output_dir: str = "data/raw/publications") -> Optional[str]:
        """Downloads digital PDF from DSpace to local disk."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        filename = Path(urllib.parse.urlparse(pdf_url).path).name
        if not filename.endswith(".pdf"):
            filename = f"{filename}.pdf"

        dest_file = out_path / filename

        try:
            resp = self.session.get(pdf_url, stream=True, timeout=20)
            resp.raise_for_status()
            with open(dest_file, "wb") as f:
                for chunk in resp.iter_content(chunk_size=16384):
                    f.write(chunk)
            return str(dest_file)
        except Exception as e:
            print(f"Error downloading PDF from {pdf_url}: {e}")
            return None
