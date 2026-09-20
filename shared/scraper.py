from __future__ import annotations

from collections import deque
from html.parser import HTMLParser
import ipaddress
import json
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
    urlopen,
)
from urllib.robotparser import RobotFileParser
from datetime import datetime, timezone


DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_MAX_LINKS = 100
DEFAULT_MAX_PAGES = 10
DEFAULT_TIMEOUT = 10
USER_AGENT = "Game-Mod-Asset-Lab/3.0"


class PageParser(HTMLParser):
    def __init__(self, base_url: str, max_items: int = DEFAULT_MAX_LINKS):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.max_items = max_items
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.headings: list[str] = []
        self.links: list[dict] = []
        self.images: list[str] = []
        self.meta: dict[str, str] = {}
        self.json_ld: list[dict | str] = []
        self.canonical: str | None = None
        self._in_title = False
        self._heading_level: str | None = None
        self._heading_parts: list[str] = []
        self._script_type: str | None = None
        self._script_parts: list[str] = []
        self._active_link: dict | None = None

    def _clean(self, value: str) -> str:
        return " ".join(value.split()).strip()

    def handle_starttag(self, tag: str, attrs):
        attributes = {str(k).lower(): (v or "") for k, v in attrs}
        tag = tag.lower()

        if tag == "title":
            self._in_title = True
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_level = tag
            self._heading_parts = []
        elif tag == "meta":
            key = attributes.get("property") or attributes.get("name")
            value = attributes.get("content")
            if key and value:
                self.meta[key.lower()] = self._clean(value)
        elif tag == "link" and attributes.get("rel", "").lower() == "canonical":
            href = attributes.get("href")
            if href:
                self.canonical = urljoin(self.base_url, href)
        elif tag == "a":
            href = attributes.get("href")
            if href and len(self.links) < self.max_items:
                absolute = urljoin(self.base_url, href)
                absolute, _ = urldefrag(absolute)
                self._active_link = {
                    "url": absolute,
                    "text_parts": [self._clean(attributes.get("title", ""))],
                }
        elif tag == "img":
            src = attributes.get("src") or attributes.get("data-src")
            if src and len(self.images) < self.max_items:
                absolute = urljoin(self.base_url, src)
                absolute, _ = urldefrag(absolute)
                self.images.append(absolute)
        elif tag == "script":
            script_type = attributes.get("type", "").lower()
            if script_type == "application/ld+json":
                self._script_type = script_type
                self._script_parts = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "a" and self._active_link is not None:
            self.links.append(
                {
                    "url": self._active_link["url"],
                    "text": self._clean(" ".join(self._active_link["text_parts"])),
                }
            )
            self._active_link = None
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading_level == tag:
            value = self._clean(" ".join(self._heading_parts))
            if value and len(self.headings) < self.max_items:
                self.headings.append(value)
            self._heading_level = None
            self._heading_parts = []
        elif tag == "script" and self._script_type == "application/ld+json":
            raw = "".join(self._script_parts).strip()
            if raw:
                try:
                    value = json.loads(raw)
                except json.JSONDecodeError:
                    value = raw
                if len(self.json_ld) < self.max_items:
                    self.json_ld.append(value)
            self._script_type = None
            self._script_parts = []

    def handle_data(self, data: str):
        cleaned = self._clean(data)
        if not cleaned:
            return
        if self._in_title:
            self.title_parts.append(cleaned)
        if self._heading_level:
            self._heading_parts.append(cleaned)
        if self._active_link is not None:
            self._active_link["text_parts"].append(cleaned)
        if self._script_type == "application/ld+json":
            self._script_parts.append(data)
        else:
            self.text_parts.append(cleaned)


def _validate_url(url: str) -> str:
    raw = url.strip()
    parsed = urlparse(raw)

    if parsed.scheme not in {"https", "http"}:
        raise ValueError("Scraper hanya mendukung HTTP/HTTPS.")
    if parsed.username or parsed.password:
        raise ValueError("URL dengan username/password tidak diizinkan.")
    if not parsed.hostname:
        raise ValueError("Hostname URL tidak ditemukan.")
    if parsed.port not in {None, 80, 443}:
        raise ValueError("Port custom tidak diizinkan.")
    if parsed.scheme == "https" and parsed.port == 80:
        raise ValueError("HTTPS harus menggunakan port 443 atau port default.")
    if parsed.scheme == "http" and parsed.port == 443:
        raise ValueError("HTTP harus menggunakan port 80 atau port default.")
    if len(raw) > 2048:
        raise ValueError("URL terlalu panjang.")

    host = parsed.hostname.lower()
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("Hostname lokal tidak diizinkan.")

    _validate_public_host(host)
    normalized = parsed._replace(fragment="")
    return urlunparse(normalized)


def _validate_public_host(host: str) -> None:
    try:
        addresses = {
            result[4][0]
            for result in socket.getaddrinfo(
                host, None, type=socket.SOCK_STREAM
            )
        }
    except socket.gaierror as exc:
        raise ValueError(f"Hostname tidak dapat di-resolve: {host}") from exc

    if not addresses:
        raise ValueError(f"Hostname tidak memiliki alamat: {host}")

    for address in addresses:
        ip = ipaddress.ip_address(address)
        if (
            not ip.is_global
            or ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_unspecified
            or ip.is_reserved
        ):
            raise ValueError("Target scraper harus berupa host publik.")


class SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe = _validate_url(urljoin(req.full_url, newurl))
        return super().redirect_request(req, fp, code, msg, headers, safe)


def _read_response(response, max_bytes: int) -> bytes:
    content_length = response.headers.get("Content-Length")
    if content_length:
        try:
            if int(content_length) > max_bytes:
                raise ValueError("Response scraper melebihi batas ukuran.")
        except ValueError as exc:
            if "melebihi" in str(exc):
                raise
    chunks = bytearray()
    while True:
        chunk = response.read(min(1024 * 1024, max_bytes - len(chunks) + 1))
        if not chunk:
            break
        chunks.extend(chunk)
        if len(chunks) > max_bytes:
            raise ValueError("Response scraper melebihi batas ukuran.")
    return bytes(chunks)


def _robots_allowed(url: str, user_agent: str, timeout: int) -> bool:
    parsed = urlparse(url)
    robots_url = urlunparse(
        (parsed.scheme, parsed.netloc, "/robots.txt", "", "", "")
    )
    try:
        request = Request(robots_url, headers={"User-Agent": user_agent})
        opener = build_opener(SafeRedirectHandler())
        with opener.open(request, timeout=timeout) as response:
            content = response.read(DEFAULT_MAX_BYTES).decode(
                response.headers.get_content_charset() or "utf-8",
                errors="replace",
            )
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(content.splitlines())
        return parser.can_fetch(user_agent, url)
    except (HTTPError, URLError, OSError, ValueError):
        return True


def scrape_page(
    url: str,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_links: int = DEFAULT_MAX_LINKS,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: str = USER_AGENT,
) -> dict:
    if not 1 <= max_bytes <= 20 * 1024 * 1024:
        raise ValueError("max_bytes harus 1 MB-20 MB.")
    if not 1 <= max_links <= 500:
        raise ValueError("max_links harus 1-500.")
    if not 1 <= timeout <= 60:
        raise ValueError("timeout harus 1-60 detik.")

    normalized_url = _validate_url(url)
    if not _robots_allowed(normalized_url, user_agent, timeout):
        raise PermissionError("robots.txt melarang scraper mengakses URL ini.")

    opener = build_opener(SafeRedirectHandler())
    request = Request(
        normalized_url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.5",
        },
    )

    try:
        with opener.open(request, timeout=timeout) as response:
            final_url = _validate_url(response.geturl())
            if not _robots_allowed(final_url, user_agent, timeout):
                raise PermissionError("robots.txt melarang URL hasil redirect.")
            content_type = response.headers.get_content_type()
            payload = _read_response(response, max_bytes)
            charset = response.headers.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            status = getattr(response, "status", 200)
    except HTTPError as exc:
        raise ValueError(f"HTTP error {exc.code}.") from exc
    except URLError as exc:
        raise ValueError(f"Gagal mengambil URL: {exc.reason}") from exc

    result = {
        "url": normalized_url,
        "final_url": final_url,
        "status": status,
        "content_type": content_type,
        "bytes": len(payload),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "title": "",
        "description": "",
        "canonical": None,
        "open_graph": {},
        "headings": [],
        "links": [],
        "images": [],
        "json_ld": [],
        "text": text[:10000],
    }

    if content_type.startswith("text/html") or content_type == "application/xhtml+xml":
        parser = PageParser(final_url, max_links)
        parser.feed(text)
        result.update(
            {
                "title": " ".join(parser.title_parts),
                "description": parser.meta.get("description", ""),
                "canonical": parser.canonical,
                "open_graph": {
                    key[3:]: value
                    for key, value in parser.meta.items()
                    if key.startswith("og:")
                },
                "headings": parser.headings,
                "links": parser.links,
                "images": parser.images,
                "json_ld": parser.json_ld,
                "text": " ".join(parser.text_parts)[:10000],
            }
        )
    elif content_type == "application/json" or final_url.endswith(".json"):
        try:
            result["json"] = json.loads(text)
        except json.JSONDecodeError:
            result["json_text"] = text[:10000]

    return result


def crawl_site(
    start_url: str,
    *,
    max_pages: int = DEFAULT_MAX_PAGES,
    max_links_per_page: int = 50,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    if not 1 <= max_pages <= 25:
        raise ValueError("max_pages harus 1-25.")
    start = _validate_url(start_url)
    start_host = (urlparse(start).hostname or "").lower()

    queue = deque([start])
    visited: set[str] = set()
    pages: list[dict] = []
    errors: list[dict] = []

    while queue and len(pages) < max_pages:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        if (urlparse(current).hostname or "").lower() != start_host:
            continue

        try:
            page = scrape_page(
                current,
                max_links=max_links_per_page,
                timeout=timeout,
            )
            final_host = (urlparse(page["final_url"]).hostname or "").lower()
            if final_host != start_host:
                raise ValueError("Crawl menolak redirect ke host lain.")
            pages.append(page)
        except (ValueError, PermissionError) as exc:
            errors.append({"url": current, "error": str(exc)})
            continue

        for link in page.get("links", []):
            target = link.get("url", "")
            if not target or (urlparse(target).hostname or "").lower() != start_host:
                continue
            parsed = urlparse(target)
            if parsed.scheme not in {"http", "https"}:
                continue
            clean = urlunparse(parsed._replace(fragment=""))
            if clean not in visited and clean not in queue:
                queue.append(clean)

    return {
        "start_url": start,
        "host": start_host,
        "pages": pages,
        "errors": errors,
        "page_count": len(pages),
        "visited_count": len(visited),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
