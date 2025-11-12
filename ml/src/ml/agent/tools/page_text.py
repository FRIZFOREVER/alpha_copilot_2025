"""Utilities for fetching and processing web pages for search enrichment."""

from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def fetch_page_html(url: str, timeout: float, max_bytes: int) -> str:
    """Download HTML content for ``url`` with size and timeout guards.

    Args:
        url: Target URL.
        timeout: Total request timeout in seconds.
        max_bytes: Maximum number of response bytes to read.

    Returns:
        Raw HTML as a string (truncated to ``max_bytes`` if necessary).

    Raises:
        RuntimeError: If the request fails for any reason.
    """

    if max_bytes <= 0:
        return ""

    try:
        with httpx.Client(
            headers={"User-Agent": USER_AGENT},
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        ) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()

                collected: list[bytes] = []
                total = 0
                for chunk in response.iter_bytes():
                    if not chunk:
                        continue

                    remaining = max_bytes - total
                    if remaining <= 0:
                        break

                    if len(chunk) > remaining:
                        collected.append(chunk[:remaining])
                        total += remaining
                        break

                    collected.append(chunk)
                    total += len(chunk)

                content = b"".join(collected)
                encoding = response.encoding or "utf-8"
                return content.decode(encoding, errors="ignore")
    except httpx.HTTPError as exc:  # pragma: no cover - defensive guard
        message = f"Failed to fetch URL {url}: {exc}"
        raise RuntimeError(message) from exc

    return ""


def html_to_text(html: str) -> str:
    """Convert HTML to a normalized plain-text representation."""

    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_excerpt(text: str, query: str, *, window: int) -> str:
    """Build a context window around the first query match in ``text``.

    Args:
        text: Source text to scan.
        query: Original search query.
        window: Number of characters to include on each side of the match.

    Returns:
        A trimmed excerpt containing the query terms, or the leading portion of
        ``text`` when no match is found.
    """

    normalized = " ".join((text or "").split())
    if not normalized:
        return ""

    if window <= 0:
        return normalized

    lowered_text = normalized.lower()
    terms = [term for term in re.split(r"\s+", query.lower()) if term]

    match_index = -1
    match_length = 0
    for term in terms or [""]:
        if not term:
            continue
        idx = lowered_text.find(term)
        if idx != -1 and (match_index == -1 or idx < match_index):
            match_index = idx
            match_length = len(term)

    if match_index == -1:
        excerpt = normalized[: window * 2]
        return excerpt.strip()

    start = max(0, match_index - window)
    end = min(len(normalized), match_index + match_length + window)

    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(normalized) else ""

    snippet = normalized[start:end].strip()
    return f"{prefix}{snippet}{suffix}" if snippet else snippet


__all__ = ["fetch_page_html", "html_to_text", "build_excerpt"]

