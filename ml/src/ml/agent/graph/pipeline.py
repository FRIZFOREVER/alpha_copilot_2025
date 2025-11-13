from typing import Any, Dict, Iterator

from langgraph.graph import StateGraph, END
from ml.agent.graph.state import GraphState

from ml.utils.voice_validation import validate_voice, form_final_report
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


def run_pipeline(payload: RequestPayload) -> Iterator[ChatResponse]:

    # Create Reasoning model client
    client: ReasoningModelClient = ReasoningModelClient()
    
    # validate user request if voice 
    if payload.is_voice:
        if not validate_voice(
            voice_decoding=payload.messages.last_message_as_history(),
            reasoning_client=client
        ):
            return form_final_report(reasoning_client=client)

    # FUTURE: validate tag if tag is empty

    # Create Graph
    app: StateGraph = create_pipeline(client)

    messages: ChatHistory = payload.messages
    state: GraphState = GraphState(messages=messages)

    final: Dict[str, Any] = app.invoke(state)
