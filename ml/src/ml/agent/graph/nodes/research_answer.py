"""Finalization node for research workflow responses."""

import logging
from collections.abc import Sequence

from ml.agent.graph.state import GraphState, NextAction, ResearchObservation, ResearchTurn
from ml.agent.prompts import get_research_answer_prompt
from ml.configs.message import ChatHistory, UserProfile

logger: logging.Logger = logging.getLogger(__name__)


def _extract_payload_documents(observation: ResearchObservation) -> list[str]:
    metadata = observation.metadata
    if not metadata:
        return []

    payload = metadata.get("payload")
    documents: list[str] = []
    if payload and hasattr(payload, "get"):
        results = payload.get("results")
        if results:
            for item in results:
                if not hasattr(item, "get"):
                    continue
                title = item.get("title") or ""
                excerpt = item.get("excerpt")
                if not excerpt:
                    snippet = item.get("snippet")
                    if snippet:
                        excerpt = snippet
                    else:
                        content = item.get("content")
                        if content:
                            excerpt = content
                url = item.get("url") or ""
                pieces: list[str] = []
                if title:
                    pieces.append(title)
                if excerpt:
                    pieces.append(excerpt)
                if url:
                    pieces.append(url)
                if pieces:
                    documents.append(" — ".join(pieces))
                if len(documents) >= 6:
                    return documents
    comparison_text = metadata.get("comparison_text")
    if comparison_text:
        documents.append("Комментарий к сравнению: " + comparison_text)
    return documents


def _gather_turn_evidence(turn_history: Sequence[ResearchTurn]) -> list[str]:
    gathered: list[str] = []
    for turn in turn_history:
        observation = turn.observation
        if observation is None:
            continue
        documents = _extract_payload_documents(observation)
        for doc in documents:
            if doc not in gathered:
                gathered.append(doc)
            if len(gathered) >= 6:
                return gathered
    return gathered


def _summarize_turn_highlights(turn_history: Sequence[ResearchTurn], limit: int = 5) -> list[str]:
    """Return a concise list of highlights for the latest research turns."""

    if not turn_history:
        return []

    start_index = max(len(turn_history) - limit, 0)
    highlights: list[str] = []
    for position, turn in enumerate(turn_history[start_index:], start=start_index + 1):
        summary = turn.reasoning_summary or "Нет заметок"
        parts: list[str] = [f"Ход {position}: {summary}"]
        request = turn.request
        if request:
            parts.append(f"Инструмент: {request.tool_name} — {request.input_text}")
        observation = turn.observation
        if observation and observation.content:
            parts.append(f"Наблюдение: {observation.content}")
        highlights.append(" | ".join(parts))
    return highlights


def research_answer_node(state: GraphState) -> GraphState:
    logger.info("Entered Research answer node")
    evidence_pool: list[str] = list(state.final_answer_evidence)
    if not evidence_pool:
        evidence_pool = _gather_turn_evidence(state.turn_history)

    profile: UserProfile = state.payload.profile
    turn_highlights = _summarize_turn_highlights(state.turn_history)
    latest_notes = state.latest_reasoning or ""
    state.final_answer_draft = latest_notes

    prompt: ChatHistory = get_research_answer_prompt(
        profile=profile,
        conversation=state.payload.messages,
        turn_highlights=turn_highlights,
        latest_reasoning=latest_notes,
        evidence_snippets=evidence_pool,
    )

    state.final_prompt = prompt
    state.next_action = NextAction.FINISH
    return state
