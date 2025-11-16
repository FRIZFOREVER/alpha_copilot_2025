import logging

from ml.agent.graph.state import GraphState
from ml.agent.prompts import compose_fast_final_prompt

logger: logging.Logger = logging.getLogger(__name__)


def fast_answer_node(state: GraphState) -> GraphState:
    logger.info("Entered Fast answer node")
    state.final_prompt = compose_fast_final_prompt(state)
    return state
