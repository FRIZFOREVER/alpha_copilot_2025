"""Reasoning node responsible for preparing context for research tool planning."""

import logging

from ml.agent.graph.state import GraphState, NextAction, ResearchTurn
from ml.agent.prompts import get_research_reason_prompt
from ml.agent.tools.registry import get_tool_registry
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory

logger: logging.Logger = logging.getLogger(__name__)


def reason_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Research reason node")

    available_tools = list(get_tool_registry().values())
    prompt: ChatHistory = get_research_reason_prompt(
        profile=state.payload.profile,
        conversation=state.payload.messages,
        turn_history=state.turn_history,
        evidence_snippets=state.final_answer_evidence,
        latest_reasoning=state.latest_reasoning_text,
        available_tools=available_tools,
    )

    reasoning_text = client.call(messages=prompt)
    logger.info("Research reasoning note prepared")

    turn = ResearchTurn(reasoning_summary=reasoning_text)
    state.turn_history.append(turn)
    state.latest_reasoning_text = reasoning_text
    state.active_tool_request = None
    state.next_action = NextAction.REQUEST_TOOL

    return state
