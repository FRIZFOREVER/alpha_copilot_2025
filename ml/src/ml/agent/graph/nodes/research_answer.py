"""Finalization node for research workflow responses."""

from collections.abc import Sequence
import logging

from ml.agent.graph.state import GraphState, NextAction, ResearchObservation, ResearchTurn
from ml.agent.prompts import get_research_answer_prompt
from ml.configs.message import ChatHistory

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


def research_answer_node(state: GraphState) -> GraphState:
    logger.info("Entered Research answer node")
    draft = state.final_answer_draft
    if draft is None:
        draft = state.latest_reasoning or ""

    evidence_pool: list[str] = list(state.final_answer_evidence)
    if not evidence_pool:
        evidence_pool = _gather_turn_evidence(state.turn_history)

    prompt: ChatHistory = get_research_answer_prompt(
        system_prompt=state.payload.system,
        conversation=state.payload.messages,
        turn_history=state.turn_history,
        answer_draft=draft,
        evidence_snippets=evidence_pool,
    )

    state.final_prompt = prompt
    state.next_action = NextAction.FINISH
    return state
