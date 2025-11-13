from ml.agent.graph.state import GraphState
from ml.api.ollama_calls import ReasoningModelClient

def thinking_planner_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    # TODO: implement Thinking planner with tool calls and structured output
    return state