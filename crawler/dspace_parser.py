import re
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Tuple

class DSpaceParser:
    """
    Robust DSpace HTML and Metadata Parser for NCPOR/NPDC Institutional Repositories.
    Supports both standard presentation layout and Dublin Core full-item layout.
    """

    @staticmethod
    def canonicalize_url(url: str, base_url: str = "") -> str:
        """Normalizes URLs, resolves relative paths, strips session tokens and fragments."""
        if base_url:
            url = urllib.parse.urljoin(base_url, url)

        parsed = urllib.parse.urlsplit(url)
        clean_path = re.sub(r';jsessionid=[A-Za-z0-9]+', '', parsed.path)
        clean_path = re.sub(r'/+', '/', clean_path)

        canonical = urllib.parse.urlunsplit((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            clean_path,
            parsed.query,
            ""
        ))
        return canonical

    @classmethod
    def is_allowed_url(cls, url: str, allowed_domains: List[str]) -> bool:
        """Validates that a URL is in-scope and not a static asset or administrative route."""
        parsed = urllib.parse.urlsplit(url)
        netloc = parsed.netloc.lower()

        if not any(domain.lower() in netloc for domain in allowed_domains):
            return False

        static_exts = ('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.ttf')
        if parsed.path.lower().endswith(static_exts):
            return False

        disallowed_routes = ['/login', '/register', '/feedback', '/forgot', '/password', '/admin', '/mydspace', '/subscribe', '/profile']
        if any(r in parsed.path.lower() for r in disallowed_routes):
            return False

        return True

    @classmethod
    def is_item_page(cls, soup: BeautifulSoup, url: str) -> bool:
        if not re.search(r'/handle/\d+/\d+', url):
            return False

        if soup.find('table', class_='dublinCore'):
            return True

        text_content = soup.get_text()
        has_metadata_fields = any(f in text_content for f in ['Title:', 'Authors:', 'Issue Date:', 'Appears in Collections:'])
        has_files_section = 'Files in This Item' in text_content or 'itemDisplayTable' in str(soup)

        return has_metadata_fields or has_files_section

    @classmethod
    def parse_item_page(cls, html: str, url: str) -> Optional[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        if not cls.is_item_page(soup, url):
            return None

        handle_match = re.search(r'/handle/(\d+)/(\d+)', url)
        if handle_match:
            prefix, suffix = handle_match.groups()
            item_id = f"DSPACE-{prefix}-{suffix}"
            handle_url = f"http://14.139.119.23:8080/dspace/handle/{prefix}/{suffix}"
        else:
            item_id = f"DSPACE-{abs(hash(url))}"
            handle_url = url

        metadata: Dict[str, Any] = {
            "item_id": item_id,
            "title": "",
            "authors": "",
            "year": None,
            "issue_date": "",
            "keywords": [],
            "abstract": "",
            "series_report_no": "",
            "collection": "",
            "expedition": "",
            "hierarchy": [],
            "handle_url": handle_url,
            "handle_uri": "",
            "pdf_attachments": [],
            "primary_pdf_url": "",
            "raw_url": url
        }

        hierarchy = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if '/handle/' in href and text and text not in ['Show full item record', 'Show simple item record']:
                if 'Scientific Report' in text or 'Expedition' in text:
                    metadata["expedition"] = text
                hierarchy.append(text)
        metadata["hierarchy"] = list(dict.fromkeys(hierarchy))

        for tr in soup.find_all('tr'):
            tds = tr.find_all(['td', 'th'])
            if len(tds) >= 2:
                k = tds[0].get_text(strip=True).replace(':', '').strip().lower()
                v = tds[1].get_text(' ', strip=True).strip()

                if k in ['title', 'dc.title']:
                    metadata["title"] = v
                elif k in ['author', 'authors', 'contributor.author', 'dc.contributor.author']:
                    metadata["authors"] = v
                elif k in ['issue date', 'date.issued', 'dc.date.issued']:
                    metadata["issue_date"] = v
                elif k in ['keywords', 'subject', 'dc.subject']:
                    words = [w.strip() for w in re.split(r'[,;]|\s{2,}', v) if w.strip()]
                    metadata["keywords"].extend(words)
                elif k in ['abstract', 'description.abstract', 'dc.description.abstract']:
                    metadata["abstract"] = v
                elif k in ['series/report no.', 'series/report no', 'relation.ispartofseries']:
                    metadata["series_report_no"] = v
                elif k in ['uri', 'identifier.uri', 'dc.identifier.uri']:
                    metadata["handle_uri"] = v
                elif k in ['appears in collections', 'collection']:
                    metadata["collection"] = v

        if not metadata["title"]:
            title_tag = soup.find('title')
            if title_tag:
                clean_title = re.sub(r'^DSPACE\s*AT\s*NCAOR:\s*', '', title_tag.text.strip(), flags=re.I)
                clean_title = re.sub(r'^Item\s+\d+/\d+', '', clean_title).strip()
                if clean_title:
                    metadata["title"] = clean_title

        metadata["keywords"] = list(dict.fromkeys(metadata["keywords"]))
        year_cand = None
        for kw in metadata["keywords"]:
            if re.match(r'^(19\d\d|20\d\d)$', kw):
                year_cand = int(kw)
                break
        if not year_cand and metadata["issue_date"]:
            m_yr = re.search(r'\b(19\d\d|20\d\d)\b', metadata["issue_date"])
            if m_yr:
                year_cand = int(m_yr.group(1))
        metadata["year"] = year_cand

        attachments = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            link_text = a.get_text(strip=True)
            if '/bitstream/' in href:
                abs_bitstream = cls.canonicalize_url(href, url)
                filename = urllib.parse.unquote(href.split('/')[-1])
                parent_tr = a.find_parent('tr')
                size_str = ""
                fmt_str = ""
                if parent_tr:
                    row_cells = [c.get_text(strip=True) for c in parent_tr.find_all(['td', 'th'])]
                    for c in row_cells:
                        if any(unit in c.lower() for unit in ['kb', 'mb', 'bytes']):
                            size_str = c
                        if 'pdf' in c.lower() or 'adobe' in c.lower():
                            fmt_str = c

                attachments.append({
                    "filename": filename,
                    "bitstream_url": abs_bitstream,
                    "link_text": link_text,
                    "size_text": size_str,
                    "format_text": fmt_str
                })

        unique_attachments = []
        seen_urls = set()
        for att in attachments:
            if att["bitstream_url"] not in seen_urls:
                seen_urls.add(att["bitstream_url"])
                unique_attachments.append(att)

        metadata["pdf_attachments"] = unique_attachments
        if unique_attachments:
            metadata["primary_pdf_url"] = unique_attachments[0]["bitstream_url"]

        return metadata

    @classmethod
    def extract_links(cls, html: str, current_url: str, allowed_domains: List[str]) -> List[Tuple[str, str]]:
        soup = BeautifulSoup(html, 'html.parser')
        links: List[Tuple[str, str]] = []
        seen = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            canon = cls.canonicalize_url(href, current_url)

            if canon in seen:
                continue
            seen.add(canon)

            if not cls.is_allowed_url(canon, allowed_domains):
                continue

            if '/bitstream/' in canon:
                ltype = "bitstream"
            elif '/handle/' in canon:
                ltype = "handle"
            elif 'community-list' in canon:
                ltype = "community_list"
            elif 'simple-search' in canon or 'browse' in canon:
                ltype = "search_browse"
            else:
                ltype = "navigation"

            links.append((canon, ltype))

        return links
