"""Pass-through node that lets the pipeline expose the final prompt for streaming."""

import logging

from ml.agent.graph.state import GraphState

logger: logging.Logger = logging.getLogger(__name__)


def final_answer_node(state: GraphState) -> GraphState:
    """Return the state unchanged so the caller can stream the final answer."""

    logger.info("Entered Final answer node")
    return state
