"""Reasoning node responsible for planning the next research action."""

import logging

from ml.agent.graph.state import GraphState, ResearchTurn
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

    response_text: str = client.call(messages=prompt)

    logger.info("Reason node response: \n%s", response_text)
    state.latest_reasoning_text = response_text

    turn = ResearchTurn(reasoning_summary=response_text)
    state.turn_history.append(turn)

    logger.info("Reasoning summary ready")
    return state
