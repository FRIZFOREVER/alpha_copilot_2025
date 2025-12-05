import logging

from ml.domain.models import GraphState

logger = logging.getLogger(__name__)


def flash_memories(state: GraphState) -> GraphState:
    logger.info("Entering flash_memories node")

    # TODO: add flash memories
    return state
