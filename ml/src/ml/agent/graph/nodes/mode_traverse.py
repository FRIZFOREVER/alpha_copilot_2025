import logging

from ml.agent.graph.state import GraphState

logger: logging.Logger = logging.getLogger(__name__)


def graph_mode_node(state: GraphState) -> GraphState:
    logger.info("Entered Graph mode node")
    # TODO: Implement logic when mode is set to "auto"
    return state
