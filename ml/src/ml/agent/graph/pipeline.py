from typing import Iterator

from langgraph.graph import StateGraph, END
from ml.agent.graph.state import GraphState

from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory, RequestPayload
from ollama import ChatResponse

def create_pipeline(client: ReasoningModelClient) -> StateGraph:
    """Create the LangGraph pipeline."""
    
    # Create graph
    workflow: StateGraph = StateGraph(GraphState)
    
    # Nodes

    app: StateGraph = workflow.compile()
    
    return app


def run_pipeline_stream(payload: RequestPayload) -> Iterator[ChatResponse]:

    # Create Reasoning model client
    client: ReasoningModelClient = ReasoningModelClient()
    
    # Create Graph
    app: StateGraph = create_pipeline(client)

    messages: ChatHistory = payload.messages
    state: GraphState = GraphState(messages=messages)

    final: GraphState = app.invoke(state)
