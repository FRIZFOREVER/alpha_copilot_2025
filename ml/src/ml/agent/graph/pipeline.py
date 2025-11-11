from typing import Any, Callable, Dict, Iterator, List, Optional
from weakref import WeakKeyDictionary
from uuid import uuid4
import json

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


def _serialize_state(state: GraphState) -> str:
    """Convert GraphState into a JSON string for logging."""
    try:
        state_dict = state.model_dump(mode="json")
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to serialise GraphState for logging")
        return f"<unserializable GraphState: {exc}>"
    return json.dumps(state_dict, ensure_ascii=False)


def _wrap_graph_node(node_name: str, fn: Callable[[GraphState], GraphState]) -> Callable[[GraphState], GraphState]:
    """Wrap graph node execution with logging."""

    def _wrapped(state: GraphState) -> GraphState:
        logger.info("LangGraph node '%s' starting", node_name)
        new_state = fn(state)
        logger.info("LangGraph node '%s' completed with state update: %s", node_name, _serialize_state(new_state))
        return new_state

    return _wrapped


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
    workflow.add_node("planner", _wrap_graph_node("planner", lambda state: planner_node(state, client)))
    workflow.add_node("research", _wrap_graph_node("research", lambda state: research_node(state, client)))
    workflow.add_node("execute_tools", _wrap_graph_node("execute_tools", execute_tools_node))
    workflow.add_node("analyze", _wrap_graph_node("analyze", lambda state: analyze_results_node(state, client)))
    workflow.add_node("synthesize", _wrap_graph_node("synthesize", lambda state: synthesize_answer_node(state, client)))
    workflow.add_node("fast_answer", _wrap_graph_node("fast_answer", lambda state: fast_answer_node(state, client)))
    logger.info("LangGraph nodes registered: %s", ["planner", "research", "execute_tools", "analyze", "synthesize", "fast_answer"])
    
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


_PIPELINE_CACHE: "WeakKeyDictionary[_ReasoningModelClient, Any]" = WeakKeyDictionary()


def _get_compiled_app(client: _ReasoningModelClient):
    app = _PIPELINE_CACHE.get(client)
    if app is None:
        app = create_pipeline(client)
        _PIPELINE_CACHE[client] = app
    return app


def run_pipeline_stream(
    client: _ReasoningModelClient,
    messages: List[Dict[str, str]],
    config: Optional[Dict[str, Any]] = None
) -> Iterator[ChatResponse]:
    """Run pipeline through LangGraph and stream the final answer generation."""

    app = _get_compiled_app(client)

    # Convert payload messages to Message objects
    message_objects: List[Message] = []
    for msg in messages:
        try:
            role = Role(msg["role"])
            message_objects.append(Message(role=role, content=msg["content"]))
        except (ValueError, KeyError) as exc:  # pragma: no cover - defensive logging
            logger.warning("Invalid message format: %s, error: %s", msg, exc)
            continue

    state = GraphState(messages=message_objects)

    invoke_config = _ensure_invoke_config(config)
    final_state = app.invoke(state, config=invoke_config)
    if not isinstance(final_state, GraphState):
        final_state = GraphState.model_validate(final_state)

    final_prompt_messages = getattr(final_state, "final_prompt_messages", None)
    if not final_prompt_messages:
        final_prompt_messages = getattr(final_state, "stream_messages", None)
    if not final_prompt_messages:
        final_prompt_messages = _build_stream_messages(final_state)

    if not final_prompt_messages:
        logger.warning("No streamable messages produced by pipeline; aborting stream.")
        return

    yield from client.stream(final_prompt_messages)


def _ensure_invoke_config(config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure invoke config contains checkpointer identifiers for LangGraph."""

    if config is None:
        config = {}
    else:
        config = dict(config)

    configurable = dict(config.get("configurable") or {})
    if not any(
        key in configurable for key in ("thread_id", "checkpoint_ns", "checkpoint_id")
    ):
        configurable["thread_id"] = str(uuid4())

    config["configurable"] = configurable
    return config


def _build_stream_messages(state: GraphState) -> List[Dict[str, str]]:
    if state.mode == "research":
        user_message = _extract_last_user_message(state.messages)
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

        return [
            {"role": "system", "content": SYNTHESIS_PROMPT},
            {"role": "user", "content": f"Запрос пользователя: {user_message}\n\n{results_context}"},
        ]

    messages = [{"role": "system", "content": FAST_ANSWER_PROMPT}]
    for msg in state.messages:
        messages.append({
            "role": msg.role.value,
            "content": msg.content,
        })

    return messages


def _extract_last_user_message(messages: List[Message]) -> str:
    for msg in reversed(messages):
        if msg.role == Role.user:
            return msg.content
    return ""
