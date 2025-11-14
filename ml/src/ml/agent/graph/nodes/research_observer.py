"""Observation processing node for the research workflow."""

from typing import Any, Dict, List

from ml.agent.graph.state import GraphState, NextAction, ResearchTurn
from ml.agent.prompts import get_research_observation_prompt
from ml.api.ollama_calls import ReasoningModelClient

MAX_RESEARCH_ITERATIONS = 6


def _extract_result_documents(payload: Dict[str, Any]) -> List[str]:
    documents: List[str] = []
    results = payload.get("results") if payload else None
    if results:
        for index, item in enumerate(results, start=1):
            lines: List[str] = []
            title = item.get("title")
            url = item.get("url")
            excerpt = item.get("excerpt")
            if not excerpt:
                snippet = item.get("snippet")
                if snippet:
                    excerpt = snippet
                else:
                    content = item.get("content")
                    if content:
                        excerpt = content
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


def _collect_documents(observation_metadata: Dict[str, Any]) -> List[str]:
    documents: List[str] = []
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
    observation = state.active_observation
    if observation is None:
        state.next_action = NextAction.THINK
        return state

    documents = _collect_documents(observation.metadata)

    prompt = get_research_observation_prompt(
        conversation=state.payload.messages,
        turn_history=state.turn_history,
        tool_name=observation.tool_name,
        documents=documents,
    )

    summary = client.call(messages=prompt)

    current_turn: ResearchTurn
    if state.turn_history:
        current_turn = state.turn_history.pop()
    else:
        current_turn = ResearchTurn()

    current_turn.observation = observation
    current_turn.reasoning_summary = summary

    state.latest_reasoning = summary
    state.active_observation = None
    state.loop_counter = state.loop_counter + 1

    state.turn_history.append(current_turn)

    if state.loop_counter < MAX_RESEARCH_ITERATIONS and state.final_prompt is None:
        state.next_action = NextAction.THINK
    else:
        state.next_action = NextAction.FINISH

    return state
