import logging

from ml.agent.graph.state import GraphState
from ml.agent.prompts import get_fast_answer_prompt

logger: logging.Logger = logging.getLogger(__name__)


def fast_answer_node(state: GraphState) -> GraphState:
    logger.info("Entered Fast answer node")
    state.final_prompt = get_fast_answer_prompt(state.payload.messages)
    return state
