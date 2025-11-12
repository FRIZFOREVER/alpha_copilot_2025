from typing import Any, Dict, Iterator, List, Optional
from weakref import WeakKeyDictionary
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ml.agent.graph.state import GraphState
from ml.agent.graph.nodes import (
    planner_node,
    research_node,
    execute_tools_node,
    extract_evidence_node,
    analyze_results_node,
    synthesize_answer_node,
    fast_answer_node,
)
from ml.api.ollama_calls import _ReasoningModelClient
from ml.configs.message import Message, Role
from ml.agent.prompts.synthesis_prompt import PROMPT as SYNTHESIS_PROMPT
from ml.agent.prompts.fast_answer_prompt import PROMPT as FAST_ANSWER_PROMPT
from ml.agent.graph.nodes.evidence import format_evidence_context
from ollama import ChatResponse

def route_after_planner(state: GraphState) -> str:
    """Route after planner based on mode."""
    if state.mode == "research":
        next_node = "research"
    else:
        next_node = "fast_answer"

    state.record_event("route.after_planner", next_node=next_node)

    return next_node


def route_after_analyze(state: GraphState) -> str:
    """Route after analysis based on whether more research is needed."""
    if state.needs_more_research:
        next_node = "research"  # Go back to research
    else:
        next_node = "synthesize"  # Synthesize final answer

    state.record_event("route.after_analyze", next_node=next_node)

    return next_node


def create_pipeline(client: _ReasoningModelClient) -> StateGraph:
    """Create the LangGraph pipeline."""
    
    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("planner", lambda state: planner_node(state, client))
    workflow.add_node("research", lambda state: research_node(state, client))
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("extract_evidence", lambda state: extract_evidence_node(state, client))
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
    workflow.add_edge("execute_tools", "extract_evidence")
    workflow.add_edge("extract_evidence", "analyze")
    
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
    invalid_messages: List[Dict[str, Any]] = []
    for msg in messages:
        try:
            role = Role(msg["role"])
            message_objects.append(Message(role=role, content=msg["content"]))
        except (ValueError, KeyError) as exc:  # pragma: no cover - defensive guard
            invalid_messages.append({
                "message": msg,
                "error": str(exc),
            })
            continue

    state = GraphState(messages=message_objects)
    if invalid_messages:
        state.record_event("pipeline.invalid_messages", invalid_messages=invalid_messages)

    invoke_config = _ensure_invoke_config(config)
    configurable = invoke_config.get("configurable") or {}
    state.thread_id = configurable.get("thread_id")
    state.checkpoint_namespace = configurable.get("checkpoint_ns")
    state.checkpoint_identifier = configurable.get("checkpoint_id")

    state.record_event(
        "pipeline.start",
        message_count=len(message_objects),
        configurable=invoke_config.get("configurable"),
    )

    latest_state: GraphState = state
    final_state: Optional[GraphState] = None

    for update in app.stream(state, config=invoke_config):
        for node_name, node_payload in update.items():
            node_state = _coerce_graph_state(node_payload)
            if node_state is not None:
                _sync_identifiers(node_state, latest_state)
                latest_state = node_state
                final_state = node_state

            active_state = node_state or latest_state
            if active_state is not None:
                active_state.record_event("pipeline.transition", node=node_name)

    if final_state is None:
        final_state = latest_state

    final_prompt_messages = getattr(final_state, "final_prompt_messages", None)
    if not final_prompt_messages:
        final_prompt_messages = getattr(final_state, "stream_messages", None)
    if not final_prompt_messages:
        final_prompt_messages = _build_stream_messages(final_state)

    if not final_prompt_messages:
        final_state.record_event("pipeline.no_stream_messages")
        return

    final_state.record_event(
        "pipeline.final_prompt",
        message_count=len(final_prompt_messages),
        roles=[msg.get("role") for msg in final_prompt_messages],
        messages=final_prompt_messages,
    )

    yield from client.stream(final_prompt_messages)


def _ensure_invoke_config(config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure invoke config contains checkpointer identifiers for LangGraph."""

    if config is None:
        config = {}
    else:
        config = dict(config)

    configurable = dict(config.get("configurable") or {})
    if not any(key in configurable for key in _IDENTIFIER_ATTRS):
        configurable["thread_id"] = str(uuid4())

    config["configurable"] = configurable
    return config


def _coerce_graph_state(payload: Any) -> Optional[GraphState]:
    if isinstance(payload, GraphState):
        return payload
    if isinstance(payload, dict):
        try:
            return GraphState.model_validate(payload)
        except Exception:  # pragma: no cover - defensive guard
            return None
    return None


_IDENTIFIER_ATTRS = {
    "thread_id": "thread_id",
    "checkpoint_ns": "checkpoint_namespace",
    "checkpoint_id": "checkpoint_identifier",
}


def _sync_identifiers(target: GraphState, reference: GraphState) -> None:
    for _, attr in _IDENTIFIER_ATTRS.items():
        ref_value = getattr(reference, attr, None)
        if ref_value and not getattr(target, attr, None):
            setattr(target, attr, ref_value)


def _build_stream_messages(state: GraphState) -> List[Dict[str, str]]:
    if state.mode == "research":
        user_message = _extract_last_user_message(state.messages)
        results_context = format_evidence_context(state)

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
