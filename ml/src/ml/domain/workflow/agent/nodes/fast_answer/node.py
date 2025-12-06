import logging

from ml.domain.models import GraphState
from ml.utils import get_system_prompt

logger = logging.getLogger(__name__)


def fast_answer(state: GraphState) -> GraphState:
    logger.info("Entering fast_answer node")

    system_prompt: str = get_system_prompt(state.user, evidence=state.evidence_list)

    state.chat.add_or_change_system(system_prompt)

    state.final_prompt = state.chat

    return state
