from ml.domain.models import GraphState
from ml.utils import get_system_prompt


def fast_answer(state: GraphState) -> GraphState:
    system_prompt: str = get_system_prompt(state.user)

    state.chat.add_or_change_system(system_prompt)

    return state
