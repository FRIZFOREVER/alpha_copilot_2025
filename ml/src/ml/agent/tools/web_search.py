from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ddgs import DDGS
from pydantic import BaseModel, Field

from ml.agent.tools import page_text
from ml.agent.tools.base import BaseTool, ToolResult
from ml.api.graph_history import PicsTags
from ml.api.graph_logging import get_context_answer_id, send_graph_log
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory

DEFAULT_FETCH_TIMEOUT = 5.0
DEFAULT_MAX_BYTES = 500_000
DEFAULT_EXCERPT_WINDOW = 160
DEFAULT_CONTENT_PREVIEW = 2_000


SearchResult = dict[str, Any]


logger = logging.getLogger(__name__)


def _get_domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.hostname or parsed.netloc or url


# --- URL filtering config ----------------------------------------------------


BLOCKED_DOMAINS: set[str] = {
    # Search engines — we don't want to summarize their SERP pages
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

# Paths that typically correspond to "search result pages" or utilities,
# not real content articles.
BLOCKED_PATH_PREFIXES: tuple[str, ...] = (
    "/search",
    "/images/search",
    "/news/search",
)

# Substrings that usually indicate API endpoints / caches / redirects.
BLOCKED_URL_SUBSTRINGS: tuple[str, ...] = (
    "/w/api.php",  # Wikipedia API, not article
    "webcache.googleusercontent.com",
    "translate.google.",
    "://r.search.yahoo.com",
)

# File extensions where HTML summarization is pointless / risky.
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


class PageSummaryResponse(BaseModel):
    """Structured summary returned by the local LLM."""

    is_information_viable: bool = Field(
        description="Whether the page contains information relevant to the user's request.",
    )
    summarization: str = Field(
        description="Detailed summary of all relevant information extracted from the page.",
    )


@dataclass
class FetchedPage:
    """Container for raw page text and summarization metadata."""

    text: str
    summary: str
    is_viable: bool


class WebSearchTool(BaseTool):
    """DuckDuckGo web search tool."""

    def __init__(
        self,
        max_results: int = 3,
        *,
        fetch_timeout: float = DEFAULT_FETCH_TIMEOUT,
        max_bytes: int = DEFAULT_MAX_BYTES,
        excerpt_window: int = DEFAULT_EXCERPT_WINDOW,
        content_preview: int = DEFAULT_CONTENT_PREVIEW,
        reasoning_client: ReasoningModelClient | None = None,
    ):
        self._max_results = max_results
        self._fetch_timeout = fetch_timeout
        self._max_bytes = max_bytes
        self._excerpt_window = excerpt_window
        self._content_preview = content_preview
        self._reasoning_client = reasoning_client or ReasoningModelClient()

    def _log_web_activity(self, message: str) -> None:
        answer_id = get_context_answer_id()
        if not send_graph_log(PicsTags.Web, answer_id, message):
            logger.debug("Graph log dispatcher unavailable for web activity: %s", message)

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Поиск информации в интернете с помощью DuckDuckGo. Возвращает результаты поиска с "
            "заголовками, ссылками и краткими описаниями."
        )

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос. Составляй "
                    "с точки зрения использования как обычный пользователь",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        }

    # --------------------------------------------------------------------- #
    # Main execution
    # --------------------------------------------------------------------- #

    def execute(self, query: str, **kwargs: Any) -> ToolResult:
        """
        Execute web search.

        Args:
            query: Search query string

        Returns:
            ToolResult with search results
        """
        self._log_web_activity("Изучаю интернет")
        try:
            with DDGS() as ddgs:  # type: ignore
                raw_results = list(
                    ddgs.text(
                        query,
                        max_results=self._max_results,
                        region="ru-ru",
                        safesearch="on",
                    )
                )

            formatted_results = self._format_results(raw_results)
            filtered_results = self._filter_results_by_url(formatted_results)

            if not filtered_results:
                logger.info(
                    "WebSearchTool: all %d raw results were filtered out as bad URLs for query=%r",
                    len(formatted_results),
                    query,
                )
                return ToolResult(
                    success=True,
                    data={
                        "query": query,
                        "results": [],
                        "count": 0,
                    },
                )

            self._enrich_results(filtered_results, query)

            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": filtered_results,
                    "count": len(filtered_results),
                },
            )
        except Exception as e:
            logger.exception("WebSearchTool.execute failed for query=%r", query)
            return ToolResult(success=False, data=None, error=str(e))

    # --------------------------------------------------------------------- #
    # Result formatting & URL filtering
    # --------------------------------------------------------------------- #

    def _format_results(self, results: Iterable[dict[str, Any]]) -> list[SearchResult]:
        """Convert raw DDGS results into a unified internal structure."""
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

    def _filter_results_by_url(self, results: list[SearchResult]) -> list[SearchResult]:
        """
        Drop obviously bad URLs before we fetch/summarize them.

        Guards against:
        - pure search result pages (Bing / Google / DDG / etc.),
        - Wikipedia API endpoints,
        - caches / translations / redirect helpers,
        - binary downloads and similar non-HTML targets.
        """
        filtered: list[SearchResult] = []

        for result in results:
            url = result.get("url")
            if not url:
                continue

            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            path = parsed.path or ""

            # 1) Block whole domains (search portals etc.)
            if netloc in BLOCKED_DOMAINS:
                logger.debug("Filtered URL by domain: %s", url)
                continue

            # 2) Block obvious search/result utility paths
            lowered_path = path.lower()
            if any(lowered_path.startswith(prefix) for prefix in BLOCKED_PATH_PREFIXES):
                logger.debug("Filtered URL by path prefix: %s", url)
                continue

            # 3) Block specific URL substrings (API endpoints, caches...)
            lowered_url = url.lower()
            if any(substr in lowered_url for substr in BLOCKED_URL_SUBSTRINGS):
                logger.debug("Filtered URL by url substring: %s", url)
                continue

            # 4) Block clearly non-HTML binary-like extensions
            suffix = Path(path).suffix.lower()
            if suffix in BLOCKED_FILE_EXTENSIONS:
                logger.debug("Filtered URL by file extension %s: %s", suffix, url)
                continue

            # If nothing triggered — keep the result
            filtered.append(result)

        logger.info(
            "WebSearchTool: filtered %d → %d results by URL guards",
            len(results),
            len(filtered),
        )
        return filtered

    # --------------------------------------------------------------------- #
    # Enrichment (fetch + summarization)
    # --------------------------------------------------------------------- #

    def _enrich_results(self, results: list[SearchResult], query: str) -> None:
        if not results:
            return

        for result in results:
            url = result.get("url")
            if not url:
                continue

            try:
                page = self._fetch_text(url, query)
            except Exception as exc:  # pragma: no cover - defensive fallback
                logger.exception("Failed to fetch/summarize URL %s", url)
                errors = result.setdefault("errors", [])
                if isinstance(errors, list):
                    errors.append(str(exc))
                else:
                    result["errors"] = [str(exc)]
                continue

            if not page.text:
                continue

            excerpt = page_text.build_excerpt(
                page.text,
                query,
                window=self._excerpt_window,
            )
            if excerpt:
                result["excerpt"] = excerpt

            preview = page.text[: self._content_preview]
            if preview:
                result["content"] = preview

            result["is_viable"] = page.is_viable
            if page.summary and page.is_viable:
                result["summary"] = page.summary
                result["content"] = page.summary

        for result in results:
            if not result.get("excerpt"):
                result["excerpt"] = result.get("snippet", "")

    # --------------------------------------------------------------------- #
    # Page fetching & LLM summarization
    # --------------------------------------------------------------------- #

    def _fetch_text(self, url: str, query: str) -> FetchedPage:
        html = page_text.fetch_page_html(
            url,
            timeout=self._fetch_timeout,
            max_bytes=self._max_bytes,
        )
        text = page_text.html_to_text(html)
        summary = ""
        is_viable = False

        domain = _get_domain_from_url(url)
        if text:
            try:
                summary_response = self._summarize_text(text, query, domain)
            except Exception:
                logger.exception("Failed to summarize page %s", url)
            else:
                summary = summary_response.summarization
                is_viable = summary_response.is_information_viable
                logger.info(
                    "Page summary for %s (viable=%s): %s",
                    url,
                    is_viable,
                    summary,
                )

        return FetchedPage(text=text, summary=summary, is_viable=is_viable)

    def _summarize_text(self, text: str, query: str, domain: str) -> PageSummaryResponse:
        self._log_web_activity(f"Изучаю {domain}")
        prompt = ChatHistory()

        prompt.add_or_change_system(
            "Вы — вдумчивый исследователь-ассистент. Оцените, содержит ли эта страница "
            "сведения, непосредственно отвечающие на запрос пользователя. "
            "Если релевантная информация есть, структурируйте результаты так, чтобы они точно "
            "соответствовали требуемой схеме JSON и не теряли важных деталей. Допускается "
            "использовать списки, таблицы и другие удобные форматы до тех пор, пока они остаются "
            "типом string.\n\n"
            "Если страница не содержит полезных данных по запросу, признавайте её неактуальной: "
            "установите is_information_viable = false и верните пустую строку в summarization.\n\n"
            "Особый случай — ПОШАГОВЫЕ ИНСТРУКЦИИ, ГАЙДЫ и РЕЦЕПТЫ:\n"
            "- Если на странице есть один явно основной рецепт/гайд, перенеси его шаги в summarizat"
            "ion "
            "максимально близко к оригиналу (можно копировать формулировки шагов дословно), но не "
            "копируй весь остальной текст страницы.\n"
            "- Если рецептов или инструкций много, выбери 1–2 наиболее релевантных запросу пользова"
            "теля "
            "и перенеси только их шаги в summarization. Остальные рецепты можно кратко упомянуть, "
            "но не "
            "копировать полностью.\n"
            "- Не копируй в summarization рекламные блоки, меню сайта,"
            " комментарии и прочий сервисный текст.\n\n"
            "Всегда следуй схеме JSON, будь избирателен: копируй дословно только действительно "
            "важные шаги "
            "рецептов/инструкций, а не всю страницу целиком."
        )

        prompt.add_user(
            "Обрабатываемые данные:\n"
            f"Домен страницы: {domain}\n"
            f"Поисковый запрос: {query}\n\n"
            f"Содержимое страницы:\n{text}"
        )

        logger.info("Summarizing page content for domain: %s", domain)

        summary_response: PageSummaryResponse = self._reasoning_client.call_structured(
            messages=prompt,
            output_schema=PageSummaryResponse,
            # num_predict=2048,
        )
        logger.info(
            "Summarization response (viable=%s): %s",
            summary_response.is_information_viable,
            summary_response.summarization,
        )
        return summary_response
