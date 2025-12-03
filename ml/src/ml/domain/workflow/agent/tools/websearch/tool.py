from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from duckduckgo_search import DDGS

from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models.tools_data import ToolResult
from ml.domain.workflow.agent.tools.base_tool import BaseTool

from .prompt import get_relevance_prompt
from .schema import ChunkRelevance
from .text_extraction import extract_text_from_url, is_url_allowed, split_into_chunks

logger = logging.getLogger(__name__)


@dataclass
class SearchHit:
    url: str
    title: str
    snippet: str


class WebSearchTool(BaseTool):
    """Web search tool that collects relevant content from the internet."""

    def __init__(self, *, max_results: int = 3) -> None:
        self.max_results = max_results

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Searches the web and returns aggregated findings."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковой запрос, который нужно исследовать.",
                }
            },
            "required": ["query"],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        query_argument = kwargs.get("query")
        if not isinstance(query_argument, str):
            raise ValueError("web_search tool requires 'query' argument of type string")

        search_hits = self._perform_search(query_argument)

        relevant_documents: list[dict[str, str]] = []
        for hit in search_hits:
            relevant_text = self._gather_relevant_text(query_argument, hit)
            if relevant_text:
                relevant_documents.append(
                    {"url": hit.url, "title": hit.title, "content": relevant_text}
                )

        return ToolResult(success=True, data={"query": query_argument, "results": relevant_documents})

    def _perform_search(self, query: str) -> list[SearchHit]:
        collected: list[SearchHit] = []
        with DDGS() as client:
            raw_results = client.text(query, max_results=10)

        for raw_result in raw_results:
            if "href" not in raw_result:
                raise ValueError("DuckDuckGo result is missing 'href' field")
            if "title" not in raw_result:
                raise ValueError("DuckDuckGo result is missing 'title' field")
            if "body" not in raw_result:
                raise ValueError("DuckDuckGo result is missing 'body' field")

            url = raw_result["href"]
            title = raw_result["title"]
            snippet = raw_result["body"]

            if not isinstance(url, str) or not isinstance(title, str) or not isinstance(snippet, str):
                raise TypeError("DuckDuckGo result fields must be strings")

            if not is_url_allowed(url):
                continue

            collected.append(SearchHit(url=url, title=title, snippet=snippet))

            if len(collected) >= self.max_results:
                break

        return collected

    def _gather_relevant_text(self, query: str, hit: SearchHit) -> str:
        try:
            document_text = extract_text_from_url(hit.url)
        except Exception:
            logger.exception("Failed to extract text from URL: %s", hit.url)
            return ""

        chunks = split_into_chunks(document_text, chunk_size=1000, overlap=128)
        if not chunks:
            return ""

        relevant_chunks = self._filter_relevant_chunks(query, chunks)
        return "\n\n".join(relevant_chunks)

    def _filter_relevant_chunks(self, query: str, chunks: list[str]) -> list[str]:
        return asyncio.run(self._evaluate_chunk_relevance(query, chunks))

    async def _evaluate_chunk_relevance(self, query: str, chunks: list[str]) -> list[str]:
        client = ReasoningModelClient.instance()
        selected: list[str] = []

        for chunk in chunks:
            prompt = get_relevance_prompt(query=query, chunk=chunk)
            result: ChunkRelevance = await client.call_structured(
                messages=prompt, output_schema=ChunkRelevance
            )

            if result.is_chunk_relevant:
                selected.append(chunk)

        return selected
