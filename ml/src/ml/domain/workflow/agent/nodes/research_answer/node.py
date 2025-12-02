from ml.domain.models import GraphState
from ml.utils import format_research_observations, get_system_prompt


def research_answer(state: GraphState) -> GraphState:
    if not state.observations:
        raise RuntimeError("Cannot craft research answer without observations")

    prompt = state.chat

    system_prompt: str = get_system_prompt(state.user)
    prompt.add_or_change_system(system_prompt)

    summary = format_research_observations(state.observations)
    prompt.add_assistant(f"Research observations:\n{summary}")

    state.final_prompt = prompt

    return state
