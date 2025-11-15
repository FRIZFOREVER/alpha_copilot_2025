from __future__ import annotations

from collections.abc import Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any

from ddgs import DDGS
from ml.agent.tools import page_text
from ml.agent.tools.base import BaseTool, ToolResult

DEFAULT_FETCH_TIMEOUT = 5.0
DEFAULT_MAX_BYTES = 500_000
DEFAULT_EXCERPT_WINDOW = 160
DEFAULT_CONTENT_PREVIEW = 2_000
MAX_FETCH_WORKERS = 5


SearchResult = dict[str, Any]


class WebSearchTool(BaseTool):
    """DuckDuckGo web search tool."""

    def __init__(
        self,
        max_results: int = 5,
        *,
        fetch_timeout: float = DEFAULT_FETCH_TIMEOUT,
        max_bytes: int = DEFAULT_MAX_BYTES,
        excerpt_window: int = DEFAULT_EXCERPT_WINDOW,
        content_preview: int = DEFAULT_CONTENT_PREVIEW,
    ):
        self._max_results = max_results
        self._fetch_timeout = fetch_timeout
        self._max_bytes = max_bytes
        self._excerpt_window = excerpt_window
        self._content_preview = content_preview

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Поиск информации в интернете с помощью DuckDuckGo. Возвращает результаты поиска с заголовками, ссылками и краткими описаниями."

    @property
    def schema(self) -> dict[str, Any]:
        # TODO: Поменять на Pydantic (наврное)
        return {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Поисковый запрос"}},
            "required": ["query"],
            "additionalProperties": False,
        }

    def execute(self, query: str, **kwargs: Any) -> ToolResult:
        """
        Execute web search.

        Args:
            query: Search query string

        Returns:
            ToolResult with search results
        """
        try:
            with DDGS() as ddgs:  # type: ignore
                results = list(ddgs.text(query, max_results=self._max_results))

            formatted_results = self._format_results(results)
            self._enrich_results(formatted_results, query)

            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": formatted_results,
                    "count": len(formatted_results),
                },
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))

    def _format_results(self, results: Iterable[dict[str, Any]]) -> list[SearchResult]:
        formatted: list[SearchResult] = []
        for result in results:
            snippet = result.get("body", "")
            formatted.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": snippet,
                    "excerpt": snippet,
                }
            )
        return formatted

    def _enrich_results(self, results: list[SearchResult], query: str) -> None:
        if not results:
            return

        max_workers = min(len(results), MAX_FETCH_WORKERS)
        if max_workers <= 0:
            return

        futures: dict[Future[str], SearchResult] = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in results:
                url = result.get("url")
                if not url:
                    continue
                futures[executor.submit(self._fetch_text, url)] = result

            for future in as_completed(futures):
                result = futures[future]
                try:
                    text = future.result()
                except Exception as exc:  # pragma: no cover - defensive fallback
                    errors = result.setdefault("errors", [])
                    if isinstance(errors, list):
                        errors.append(str(exc))
                    else:
                        result["errors"] = [str(exc)]
                    continue

                if not text:
                    continue

                excerpt = page_text.build_excerpt(
                    text,
                    query,
                    window=self._excerpt_window,
                )
                if excerpt:
                    result["excerpt"] = excerpt

                preview = text[: self._content_preview].strip()
                if preview:
                    result["content"] = preview

        for result in results:
            if not result.get("excerpt"):
                result["excerpt"] = result.get("snippet", "")

    def _fetch_text(self, url: str) -> str:
        html = page_text.fetch_page_html(
            url,
            timeout=self._fetch_timeout,
            max_bytes=self._max_bytes,
        )
        return page_text.html_to_text(html)
