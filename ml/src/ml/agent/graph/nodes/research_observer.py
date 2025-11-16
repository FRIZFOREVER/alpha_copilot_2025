"""Observation processing node for the research workflow."""

import logging
from typing import Any

from ml.agent.graph.state import GraphState, ResearchTurn
from ml.agent.prompts import (
    get_research_observation_prompt,
    summarize_conversation_for_observer,
    summarize_turn_history_for_observer,
)
from ml.api.ollama_calls import ReasoningModelClient

logger: logging.Logger = logging.getLogger(__name__)


def _extract_result_documents(payload: dict[str, Any]) -> list[str]:
    documents: list[str] = []
    results: Any | None = payload.get("results") if payload else None
    if results:
        for index, item in enumerate(results, start=1):
            is_viable = item.get("is_viable") if hasattr(item, "get") else None
            if is_viable is False:
                continue
            lines: list[str] = []
            title = item.get("title")
            url = item.get("url")
            summary = item.get("summary")
            excerpt = item.get("excerpt")
            if not excerpt:
                snippet = item.get("snippet")
                if snippet:
                    excerpt = snippet
                else:
                    content = item.get("content")
                    if content:
                        excerpt = content
            if is_viable and summary:
                excerpt = summary
            if title:
                lines.append(f"Title: {title}")
            if url:
                lines.append(f"URL: {url}")
            if excerpt:
                lines.append(f"Details: {excerpt}")
            if lines:
                documents.append("\n".join(lines))
            else:
                documents.append(f"Result {index}: No additional details were provided.")
    return documents


def _collect_documents(observation_metadata: dict[str, Any]) -> list[str]:
    documents: list[str] = []
    payload = observation_metadata.get("payload") if observation_metadata else None
    if payload and hasattr(payload, "get"):
        documents.extend(_extract_result_documents(payload))
        query = payload.get("query")
        if query:
            documents.append(f"Original query: {query}")
    comparison_note = observation_metadata.get("comparison_text") if observation_metadata else None
    if comparison_note:
        documents.append(f"Comparison guidance: {comparison_note}")
    return documents


def research_observer_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Research observer node")
    observation = state.active_observation
    if observation is None:
        return state

    documents = _collect_documents(observation.metadata)

    if documents:
        collected: list[str] = list(state.final_answer_evidence)
        collected.extend(documents)
        state.final_answer_evidence = collected

    conversation_summary = summarize_conversation_for_observer(state.payload.messages)
    turn_history_summary = summarize_turn_history_for_observer(state.turn_history)

    prompt = get_research_observation_prompt(
        profile=state.payload.profile,
        conversation_summary=conversation_summary,
        turn_history_summary=turn_history_summary,
        tool_name=observation.tool_name,
        documents=documents,
    )

    summary: str = client.call(messages=prompt)
    logger.info("Research observer summary: %s", summary)

    current_turn: ResearchTurn
    if state.turn_history:
        current_turn = state.turn_history.pop()
    else:
        current_turn = ResearchTurn()

    current_turn.observation = observation
    current_turn.reasoning_summary = summary

    state.latest_reasoning_text = summary
    state.active_observation = None

    state.turn_history.append(current_turn)

    return state
