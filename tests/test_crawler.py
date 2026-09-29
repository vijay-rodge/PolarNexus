import io
import json
import pytest
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from crawler.dspace_parser import DSpaceParser
from crawler.state import CrawlerStateManager
from crawler.downloader import PDFDownloader
from crawler.extractor import PDFTextExtractor
from crawler.config import CrawlerConfig

SAMPLE_ITEM_133_HTML = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<head><title>DSPACE AT NCAOR: Item 123456789/133</title></head>
<body>
  <a href="/dspace/handle/123456789/122">01] Scientific Report Of First Indian Expedition To Antarctica</a>
  <a href="/dspace/handle/123456789/123">2]Meteorology, Instrument & Navigation</a>

  <table class="itemDisplayTable">
    <tr><td>Title:</td><td>Position fixing in Antarctica</td></tr>
    <tr><td>Authors:</td><td>Pathak, M.C.</td></tr>
    <tr><td>Keywords:</td><td>1983, Satellite, Longitude, Radio Propogation, frequency, polar orbits</td></tr>
    <tr><td>Issue Date:</td><td>13-Nov-2006</td></tr>
    <tr><td>Series/Report no.:</td><td>Technical Publication;1</td></tr>
    <tr><td>URI:</td><td>http://hdl.handle.net/123456789/133</td></tr>
    <tr><td>Appears in Collections:</td><td>2]Meteorology, Instrument & Navigation</td></tr>
  </table>

  <h3>Files in This Item:</h3>
  <table>
    <tr><th>File</th><th>Description</th><th>Size</th><th>Format</th><th></th></tr>
    <tr>
      <td>ARTICLE 4.pdf</td>
      <td>Technical Report</td>
      <td>137Kb</td>
      <td>Adobe PDF</td>
      <td><a href="/dspace/bitstream/123456789/133/5/ARTICLE+4.pdf">View/Open</a></td>
    </tr>
  </table>
</body>
</HTML>
"""

def test_canonicalize_url():
    raw_url = "http://14.139.119.23:8080/dspace/handle/123456789/133;jsessionid=ABC123XYZ?mode=full#section"
    canon = DSpaceParser.canonicalize_url(raw_url)
    assert ";jsessionid" not in canon
    assert "#section" not in canon
    assert canon == "http://14.139.119.23:8080/dspace/handle/123456789/133?mode=full"

def test_is_allowed_url():
    allowed = ["14.139.119.23", "14.139.119.23:8080"]
    assert DSpaceParser.is_allowed_url("http://14.139.119.23:8080/dspace/handle/123456789/122", allowed) is True
    assert DSpaceParser.is_allowed_url("http://14.139.119.23:8080/dspace/styles.css", allowed) is False
    assert DSpaceParser.is_allowed_url("http://google.com/search", allowed) is False
    assert DSpaceParser.is_allowed_url("http://14.139.119.23:8080/dspace/login", allowed) is False

def test_parse_item_page_position_fixing():
    url = "http://14.139.119.23:8080/dspace/handle/123456789/133"
    metadata = DSpaceParser.parse_item_page(SAMPLE_ITEM_133_HTML, url)

    assert metadata is not None
    assert metadata["item_id"] == "DSPACE-123456789-133"
    assert metadata["title"] == "Position fixing in Antarctica"
    assert metadata["authors"] == "Pathak, M.C."
    assert metadata["year"] == 1983
    assert metadata["series_report_no"] == "Technical Publication;1"
    assert "Meteorology" in metadata["collection"]
    assert len(metadata["pdf_attachments"]) == 1
    assert metadata["primary_pdf_url"] == "http://14.139.119.23:8080/dspace/bitstream/123456789/133/5/ARTICLE+4.pdf"

def test_state_resumability(tmp_path):
    db_file = tmp_path / "test_state.db"
    manager = CrawlerStateManager(db_file)

    u1 = "http://14.139.119.23:8080/dspace/handle/123456789/122"
    assert manager.add_url(u1, u1, depth=0, url_type="collection") is True
    assert manager.add_url(u1, u1, depth=0, url_type="collection") is False

    queued = manager.get_queued_urls(10)
    assert len(queued) == 1

    manager.mark_url_visited(u1, http_status=200)
    assert manager.is_url_visited(u1) is True

def test_pdf_magic_byte_sanitization():
    dirty_title = 'Report: 15th "Arctic" Expedition <Glaciology>/2019?'
    clean = PDFDownloader.sanitize_filename(dirty_title)
    assert ":" not in clean
    assert '"' not in clean
    assert "<" not in clean
    assert ">" not in clean
    assert "/" not in clean

def test_chunk_generation_and_metadata():
    extractor = PDFTextExtractor(chunk_size=100, chunk_overlap=20)
    pages_data = [{"page_number": 1, "text": "A" * 250}]
    chunks = extractor._generate_chunks(
        pages_data=pages_data,
        item_id="DSPACE-133",
        title="Position fixing in Antarctica",
        authors="Pathak, M.C.",
        year=1983,
        expedition="First Indian Expedition",
        collection="Navigation",
        source_url="http://14.139.119.23:8080/dspace/handle/123456789/133"
    )
    assert len(chunks) > 0
    assert chunks[0]["document_id"] == "DSPACE-133"
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["year"] == 1983
