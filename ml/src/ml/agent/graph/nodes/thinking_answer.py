"""Finalization node for the thinking pipeline."""

import logging

from ml.agent.graph.state import GraphState
from ml.agent.prompts import get_thinking_answer_prompt

logger: logging.Logger = logging.getLogger(__name__)


def thinking_answer_node(state: GraphState) -> GraphState:
    logger.info("Entered Thinking answer node")
    prompt = get_thinking_answer_prompt(
        messages=state.payload.messages,
        profile=state.payload.profile,
        final_answer_evidence=state.final_answer_evidence,
    )

    state.final_prompt = prompt
    logger.info("Thinking answer final prompt:\n%s", prompt.model_dump_string())
    return state
