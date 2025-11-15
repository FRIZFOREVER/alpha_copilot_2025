import logging

from ml.agent.graph.state import GraphState

logger: logging.Logger = logging.getLogger(__name__)


def fast_answer_node(state: GraphState) -> GraphState:
    logger.info("Entered Fast answer node")
    if state.final_prompt is None:
        state.final_prompt = state.payload.messages
    return state
