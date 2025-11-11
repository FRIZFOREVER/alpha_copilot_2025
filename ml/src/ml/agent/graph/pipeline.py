from typing import Dict, Any, Iterator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ml.agent.graph.state import GraphState
from ml.agent.graph.nodes import (
    planner_node,
    research_node,
    execute_tools_node,
    analyze_results_node,
    synthesize_answer_node,
    fast_answer_node,
)
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.configs.message import Message, Role
from ml.agent.prompts.synthesis_prompt import PROMPT as SYNTHESIS_PROMPT
from ml.agent.prompts.fast_answer_prompt import PROMPT as FAST_ANSWER_PROMPT
from ollama import ChatResponse
import logging

logger = logging.getLogger(__name__)


def route_after_planner(state: GraphState) -> str:
    """Route after planner based on mode."""
    if state.mode == "research":
        return "research"
    else:
        return "fast_answer"


def route_after_analyze(state: GraphState) -> str:
    """Route after analysis based on whether more research is needed."""
    if state.needs_more_research:
        return "research"  # Go back to research
    else:
        return "synthesize"  # Synthesize final answer


def create_pipeline(client: _ReasoningModelClient) -> StateGraph:
    """Create the LangGraph pipeline."""
    
    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("planner", lambda state: planner_node(state, client))
    workflow.add_node("research", lambda state: research_node(state, client))
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("analyze", lambda state: analyze_results_node(state, client))
    workflow.add_node("synthesize", lambda state: synthesize_answer_node(state, client))
    workflow.add_node("fast_answer", lambda state: fast_answer_node(state, client))
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Add edges
    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "research": "research",
            "fast_answer": "fast_answer"
        }
    )
    
    workflow.add_edge("research", "execute_tools")
    workflow.add_edge("execute_tools", "analyze")
    
    workflow.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {
            "research": "research",
            "synthesize": "synthesize"
        }
    )
    
    workflow.add_edge("synthesize", END)
    workflow.add_edge("fast_answer", END)
    
    # Compile graph
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app
def run_pipeline_stream(
    client: _ReasoningModelClient,
    messages: list[Dict[str, str]],
    config: Dict[str, Any] = None
) -> Iterator[ChatResponse]:
    """Run pipeline and stream only the final answer generation."""
    # Run pipeline up to the point where we generate the final answer
    # We'll manually execute the nodes to prepare messages for streaming
    
    # Convert messages to Message objects
    message_objects = []
    for msg in messages:
        try:
            role = Role(msg["role"])
            message_objects.append(Message(role=role, content=msg["content"]))
        except (ValueError, KeyError) as e:
            logger.warning(f"Invalid message format: {msg}, error: {e}")
            # Skip invalid messages
            continue
    
    # Initialize state and run planning
    state = GraphState(messages=message_objects)
    state = planner_node(state, client)
    
    # Prepare streaming messages based on mode
    stream_messages = []
    
    if state.mode == "research":
        # Run research pipeline
        state = research_node(state, client)
        state = execute_tools_node(state)
        state = analyze_results_node(state, client)
        
        # Continue research loop if needed
        while state.needs_more_research and state.research_iteration < state.max_research_iterations:
            state = research_node(state, client)
            state = execute_tools_node(state)
            state = analyze_results_node(state, client)
        
        # Prepare synthesis messages for streaming
        user_message = None
        for msg in reversed(state.messages):
            if msg.role == Role.user:
                user_message = msg.content
                break
        
        # Prepare search results context
        results_context = "Результаты поиска:\n\n"
        for result in state.tool_results:
            if result.get("type") == "search_result" and result.get("success"):
                search_data = result.get("data", {})
                query = search_data.get("query", "")
                results = search_data.get("results", [])
                results_context += f"Запрос: {query}\n"
                for i, res in enumerate(results, 1):
                    results_context += f"{i}. {res.get('title', '')}\n"
                    results_context += f"   URL: {res.get('url', '')}\n"
                    results_context += f"   {res.get('snippet', '')}\n\n"
        
        stream_messages = [
            {"role": "system", "content": SYNTHESIS_PROMPT},
            {"role": "user", "content": f"Запрос пользователя: {user_message}\n\n{results_context}"}
        ]
    else:
        # Fast answer mode - use conversation history
        stream_messages = [{"role": "system", "content": FAST_ANSWER_PROMPT}]
        for msg in state.messages:
            stream_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
    
    # Stream the final answer generation
    yield from client.stream(stream_messages)
