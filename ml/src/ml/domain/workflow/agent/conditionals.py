import logging

from ml.domain.models import GraphState, ModelMode

logger = logging.getLogger(__name__)


def mode_decision(state: GraphState) -> str:
    mode = state.model_mode

    if mode == ModelMode.Fast:
        return "fast_pipeline"
    if mode == ModelMode.Thiking:
        return "thinking_pipeline"
    if mode == ModelMode.Research:
        return "research_pipeline"

    msg = "Failed to branch into pipeline"
    logger.error(msg)
    raise RuntimeError(msg)


def research_decision(state: GraphState) -> str:
    return "finalize"
