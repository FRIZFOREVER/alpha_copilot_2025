import logging
from collections.abc import Iterator
from functools import partial
from typing import Any

from langgraph.graph import END, StateGraph
from ollama import ChatResponse

from ml.agent.graph.nodes import (
    fast_answer_node,
    final_answer_node,
    flash_memories_node,
    graph_mode_node,
    reason_node,
    research_answer_node,
    research_observer_node,
    research_tool_call_node,
    thinking_answer_node,
    thinking_planner_node,
)
from ml.agent.graph.state import GraphState, NextAction
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory, RequestPayload, Tag
from ml.utils.tag_validation import define_tag
from ml.utils.voice_validation import form_final_report, validate_voice

logger: logging.Logger = logging.getLogger(__name__)


def _extract_pipeline_mode(state: GraphState) -> str:
    return state.payload.mode.value


def _route_tool_or_answer(state: GraphState) -> str:
    if state.next_action == NextAction.ANSWER:
        return NextAction.ANSWER.value
    return NextAction.OBSERVATION.value


def create_pipeline(client: ReasoningModelClient) -> StateGraph:
    """Create the LangGraph pipeline."""

    # Create graph
    workflow: StateGraph = StateGraph(GraphState)

    # Nodes
    workflow.add_node("Mode Decider", partial(graph_mode_node, client=client))
    # Not implemented yet
    workflow.add_node("Flash Memories", flash_memories_node)
    workflow.add_node("Thinking planner", partial(thinking_planner_node, client=client))
    workflow.add_node("Thinking answer", thinking_answer_node)
    workflow.add_node("Research reason", partial(reason_node, client=client))
    workflow.add_node("Research tool call", partial(research_tool_call_node, client=client))
    workflow.add_node("Research observer", partial(research_observer_node, client=client))
    workflow.add_node("Research answer", partial(research_answer_node, client=client))
    workflow.add_node(
        "Fast answer", fast_answer_node
    )  # not passing model cuz forming a final prompt
    workflow.add_node("Final answer", final_answer_node)

    # entrypoint
    workflow.set_entry_point("Mode Decider")

    # Conditional graph movements
    # # General
    workflow.add_conditional_edges(
        "Mode Decider",
        _extract_pipeline_mode,
        {
            "fast": "Flash Memories",
            "thinking": "Thinking planner",
            "research": "Research reason",
        },
    )

    # # edges

    # Fast
    workflow.add_edge("Flash Memories", "Fast answer")
    workflow.add_edge("Fast answer", "Final answer")

    # Thinking
    workflow.add_edge("Thinking planner", "Thinking answer")
    workflow.add_edge("Thinking answer", "Final answer")

    # Research
    workflow.add_edge("Research reason", "Research tool call")
    workflow.add_conditional_edges(
        "Research tool call",
        _route_tool_or_answer,
        {
            NextAction.OBSERVATION.value: "Research observer",
            NextAction.ANSWER.value: "Research answer",
        },
    )
    workflow.add_edge("Research observer", "Research reason")
    workflow.add_edge("Research answer", "Final answer")

    workflow.add_edge("Final answer", END)

    app: StateGraph = workflow.compile()  # type: ignore

    return app


def run_pipeline(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
    # Create Reasoning model client
    client: ReasoningModelClient = ReasoningModelClient()

    # validate user request if voice
    if payload.is_voice:
        voice_history: ChatHistory = payload.messages.last_message_as_history()
        voice_is_valid: bool = validate_voice(
            voice_decoding=voice_history,
            reasoning_client=client,
        )
        if not voice_is_valid:
            logger.warning(
                "Voice validation failed. Returning fallback stream. Conversation: %s",
                payload.messages.model_dump_string(),
            )
            if not payload.tag:
                payload.tag = Tag.General
            logger.info("Returning fallback stream with tag %s", payload.tag.value)
            return form_final_report(reasoning_client=client), payload.tag

    # validate tag if tag is empty
    if not payload.tag:
        logger.info("Tag not found. Starting tag definition")
        payload.tag = define_tag(
            last_message=payload.messages.last_message_as_history(), reasoning_client=client
        )
        logger.info("Defined a tag: %s", payload.tag.value)

    # Create Graph
    app: StateGraph = create_pipeline(client)

    # Create initial state
    state: GraphState = GraphState(payload=payload)

    raw_result: dict[str, Any] = app.invoke(state)  # type: ignore
    try:
        result: GraphState = GraphState.model_validate(raw_result)
        logging.debug(
            "Started final prompt generation with payload: \n%s",
            result.final_prompt.model_dump_json(ensure_ascii=False, indent=2),  # type: ignore
        )
    except Exception as exc:  # pragma: no cover - validation should succeed
        logger.error(
            "Failed to validate GraphState from graph output: %s; raw_result=%s",
            exc,
            raw_result,
        )
        raise RuntimeError("GraphState validation failed") from exc

    if result.final_prompt:
        return client.stream(result.final_prompt), payload.tag

    error_message = "Graph execution finished without final prompt"
    logger.error(
        "%s; state: %s", error_message, result.model_dump_json(ensure_ascii=False, indent=2)
    )
    raise RuntimeError(error_message)
