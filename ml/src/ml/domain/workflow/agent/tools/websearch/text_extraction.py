from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

BLOCKED_DOMAINS: set[str] = {
    "www.bing.com",
    "bing.com",
    "www.google.com",
    "google.com",
    "duckduckgo.com",
    "www.duckduckgo.com",
    "search.yahoo.com",
    "yandex.ru",
    "yandex.com",
}

BLOCKED_PATH_PREFIXES: tuple[str, ...] = (
    "/search",
    "/images/search",
    "/news/search",
)

BLOCKED_URL_SUBSTRINGS: tuple[str, ...] = (
    "/w/api.php",
    "webcache.googleusercontent.com",
    "translate.google.",
    "://r.search.yahoo.com",
)

BLOCKED_FILE_EXTENSIONS: set[str] = {
    ".zip",
    ".exe",
    ".msi",
    ".7z",
    ".tar",
    ".gz",
    ".rar",
    ".iso",
    ".dmg",
    ".apk",
    ".bin",
}


def is_url_allowed(url: str) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path

    if domain in BLOCKED_DOMAINS:
        return False

    for blocked_prefix in BLOCKED_PATH_PREFIXES:
        if path.startswith(blocked_prefix):
            return False

    for blocked_substring in BLOCKED_URL_SUBSTRINGS:
        if blocked_substring in url:
            return False

    suffix = Path(path).suffix.lower()
    if suffix in BLOCKED_FILE_EXTENSIONS:
        return False

    return True


def fetch_html(url: str, *, timeout: float = 10.0) -> str:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()

    content = response.text
    if not isinstance(content, str):
        raise TypeError("Unexpected response type when fetching HTML content")

    return content


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text(" ")
    if not isinstance(text, str):
        raise TypeError("BeautifulSoup returned non-string text content")

    normalized = re.sub(r"\s+", " ", text)
    return normalized


def extract_text_from_url(url: str) -> str:
    html = fetch_html(url)
    return html_to_text(html)


def split_into_chunks(text: str, *, chunk_size: int, overlap: int) -> list[str]:
    tokens = text.split()
    if not tokens:
        return []

    chunks: list[str] = []
    start = 0
    token_count = len(tokens)

    while start < token_count:
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(" ".join(chunk_tokens))

        if end >= token_count:
            break

        start = end - overlap
        if start < 0:
            start = 0

    return chunks
