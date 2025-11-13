from ml.agent.graph.state import GraphState
from ml.agent.prompts import get_fast_answer_prompt

def fast_answer_node(state: GraphState) -> GraphState:
    state.final_prompt = get_fast_answer_prompt(state.payload.messages)
    return state