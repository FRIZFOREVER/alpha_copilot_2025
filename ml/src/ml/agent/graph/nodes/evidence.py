"""Nodes and helpers for producing structured evidence from search results."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

import logging
from pydantic import BaseModel, Field

from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.agent.prompts.evidence_prompt import PROMPT as EVIDENCE_PROMPT

logger = logging.getLogger("app.pipeline")


class EvidenceSummary(BaseModel):
    """Structured summary generated for a single search result."""

    title: str = Field(default="", description="Original title of the source")
    url: str = Field(default="", description="Canonical URL of the source")
    facts: List[str] = Field(
        default_factory=list,
        description="Concise factual bullet points extracted from the source",
    )


def extract_evidence_node(
    state: GraphState, client: _ReasoningModelClient
) -> GraphState:
    """Produce structured evidence entries for each successful search result."""

    evidence_entries: List[Dict[str, Any]] = []

    for query, result in _iterate_search_results(state.tool_results):
        title = result.get("title", "").strip()
        url = result.get("url", "").strip()
        snippet = _coalesce_snippet(result)
        content = _prepare_source_content(result)

        if not content and not snippet:
            # Nothing to summarise; skip empty results entirely.
            continue

        messages = [
            {"role": "system", "content": EVIDENCE_PROMPT},
            {
                "role": "user",
                "content": _build_evidence_payload(title=title, url=url, content=content),
            },
        ]

        summary: EvidenceSummary | None = None
        try:
            summary = client.call_structured(messages=messages, output_schema=EvidenceSummary)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Failed to summarise evidence for %s: %s", url or title, exc)

        facts: List[str] = []
        if summary:
            title = summary.title.strip() or title
            url = summary.url.strip() or url
            facts = [fact.strip() for fact in summary.facts if fact and fact.strip()]

        fallback_used = False
        if not facts:
            fallback_fact = snippet or content
            if fallback_fact:
                fallback_used = True
                truncated = fallback_fact[:280].strip()
                facts = [truncated] if truncated else []

        if not facts:
            # Skip entirely empty entries even after fallback.
            continue

        evidence_entries.append(
            {
                "title": title,
                "url": url,
                "facts": facts[:3],
                "query": query,
                "fallback": fallback_used,
            }
        )

    state.evidence = evidence_entries
    return state


def format_evidence_context(state: GraphState) -> str:
    """Return formatted context string for prompts using collected evidence."""

    if state.evidence:
        lines: List[str] = ["Результаты поиска:", ""]
        for entry in state.evidence:
            title = entry.get("title") or "Источник"
            url = entry.get("url") or ""
            query = entry.get("query")
            header_parts = [title]
            if url:
                header_parts.append(f"URL: {url}")
            if query:
                header_parts.append(f"Запрос: {query}")
            lines.append("; ".join(header_parts))
            for fact in entry.get("facts", []):
                lines.append(f"- {fact}")
            lines.append("")
        return "\n".join(lines)

    # Fallback: rebuild context from snippets if evidence is unavailable.
    lines = ["Результаты поиска:", ""]
    for query, result in _iterate_search_results(state.tool_results):
        title = result.get("title", "")
        url = result.get("url", "")
        lines.append(f"{title}")
        if url:
            lines.append(f"URL: {url}")
        if query:
            lines.append(f"Запрос: {query}")
        snippet = _coalesce_snippet(result)
        if snippet:
            lines.append(f"- {snippet}")
        lines.append("")

    return "\n".join(lines)


def _iterate_search_results(tool_results: Iterable[Dict[str, Any]]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    for result in tool_results:
        if result.get("type") != "search_result" or not result.get("success"):
            continue
        data = result.get("data") or {}
        query = data.get("query", "")
        for item in data.get("results", []) or []:
            if isinstance(item, dict):
                yield query, item


def _build_evidence_payload(title: str, url: str, content: str) -> str:
    payload_parts = []
    if title:
        payload_parts.append(f"Название: {title}")
    if url:
        payload_parts.append(f"URL: {url}")
    payload_parts.append("Контент:")
    payload_parts.append(content)
    return "\n".join(payload_parts)


def _prepare_source_content(result: Dict[str, Any]) -> str:
    segments: List[str] = []
    for key in ("content", "excerpt", "snippet"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            segments.append(value.strip())
    combined = "\n\n".join(dict.fromkeys(segments))  # Remove duplicates while preserving order
    # Keep payload compact for the reasoning model
    return combined[:2000]


def _coalesce_snippet(result: Dict[str, Any]) -> str:
    for key in ("excerpt", "snippet", "content"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


__all__ = [
    "EvidenceSummary",
    "extract_evidence_node",
    "format_evidence_context",
]

