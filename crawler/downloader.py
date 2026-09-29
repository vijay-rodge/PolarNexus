import re
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, Any, Optional

class PDFDownloader:
    """
    Production-grade streaming PDF downloader with strict validation:
    verifies HTTP status, redirect resolution, Content-Type, file size,
    and the authentic '%PDF-' binary signature.
    """

    def __init__(self, user_agent: str, timeout: int = 30, delay: float = 1.0, max_retries: int = 3):
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    @staticmethod
    def sanitize_filename(name: str, max_length: int = 80) -> str:
        clean = re.sub(r'[\\/*?:"<>|#%&{}\\<>*?/$!\'":@+`|=]+', '_', name)
        clean = re.sub(r'\s+', '_', clean).strip('._')
        if len(clean) > max_length:
            clean = clean[:max_length]
        return clean or "document"

    def download_pdf(
        self,
        pdf_url: str,
        dest_dir: Path,
        item_id: str,
        title: str = "",
        expedition: str = ""
    ) -> Dict[str, Any]:
        time.sleep(self.delay)

        exp_folder = self.sanitize_filename(expedition or "general", max_length=50)
        target_dir = dest_dir / exp_folder
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_title = self.sanitize_filename(title or "article", max_length=60)
        safe_item_id = self.sanitize_filename(item_id, max_length=30)
        dest_filename = f"{safe_item_id}_{safe_title}.pdf"
        target_file = target_dir / dest_filename

        result: Dict[str, Any] = {
            "success": False,
            "url": pdf_url,
            "resolved_url": pdf_url,
            "file_path": "",
            "sha256": "",
            "file_size": 0,
            "http_status": 0,
            "mime_type": "",
            "is_restricted": False,
            "error": None
        }

        if target_file.exists() and target_file.stat().st_size > 1000:
            with open(target_file, "rb") as f:
                header = f.read(16)
                if header.startswith(b"%PDF-"):
                    f.seek(0)
                    hasher = hashlib.sha256()
                    while chunk := f.read(65536):
                        hasher.update(chunk)
                    result["success"] = True
                    result["file_path"] = str(target_file)
                    result["sha256"] = hasher.hexdigest()
                    result["file_size"] = target_file.stat().st_size
                    result["http_status"] = 200
                    result["mime_type"] = "application/pdf"
                    return result

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with self.session.get(pdf_url, stream=True, timeout=self.timeout, allow_redirects=True) as resp:
                    result["http_status"] = resp.status_code
                    result["resolved_url"] = resp.url
                    result["mime_type"] = resp.headers.get("Content-Type", "")

                    if resp.status_code in [401, 403]:
                        result["is_restricted"] = True
                        result["error"] = f"HTTP {resp.status_code}: Access Restricted / Unauthorized"
                        return result
                    elif resp.status_code == 404:
                        result["error"] = "HTTP 404: PDF Not Found on Repository"
                        return result
                    elif resp.status_code != 200:
                        last_error = f"HTTP status {resp.status_code}"
                        time.sleep(attempt * 2.0)
                        continue

                    hasher = hashlib.sha256()
                    total_bytes = 0
                    first_chunk = True

                    with open(target_file, "wb") as f_out:
                        for chunk in resp.iter_content(chunk_size=32768):
                            if not chunk:
                                continue
                            if first_chunk:
                                if not chunk.startswith(b"%PDF-"):
                                    f_out.close()
                                    target_file.unlink(missing_ok=True)
                                    result["error"] = f"Invalid PDF signature: received non-PDF payload ({chunk[:20]!r})"
                                    return result
                                first_chunk = False

                            f_out.write(chunk)
                            hasher.update(chunk)
                            total_bytes += len(chunk)

                    if total_bytes < 500:
                        target_file.unlink(missing_ok=True)
                        result["error"] = f"Downloaded file too small ({total_bytes} bytes), rejected."
                        return result

                    result["success"] = True
                    result["file_path"] = str(target_file)
                    result["sha256"] = hasher.hexdigest()
                    result["file_size"] = total_bytes
                    return result

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                time.sleep(attempt * 2.0)

        result["error"] = f"Download failed after {self.max_retries} attempts: {last_error}"
        return result
