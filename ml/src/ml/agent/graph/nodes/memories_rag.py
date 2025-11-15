import logging

from ml.agent.graph.state import GraphState

logger: logging.Logger = logging.getLogger(__name__)


def flash_memories_node(state: GraphState) -> GraphState:
    logger.info("Entered Flash memory node")
    # Add memories tool call here and update memories evidance inside GraphState
    return state
