"""Finalization node for the thinking pipeline."""

import logging

from ml.agent.graph.state import GraphState
from ml.agent.prompts import get_thinking_answer_prompt

logger: logging.Logger = logging.getLogger(__name__)


def thinking_answer_node(state: GraphState) -> GraphState:
    logger.info("Entered Thinking answer node")
    prompt = get_thinking_answer_prompt(
        conversation=state.payload.messages,
        profile=state.payload.profile,
        plan_summary=state.thinking_plan_summary,
        plan_steps=state.thinking_plan_steps,
        thinking_evidence=state.thinking_evidence,
        final_answer_evidence=state.final_answer_evidence,
        draft=state.final_answer_draft or "",
    )

    state.final_prompt = prompt
    return state
