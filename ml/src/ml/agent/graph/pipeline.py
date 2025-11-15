import logging
from collections.abc import Iterator
from functools import partial
from typing import Any

from langgraph.graph import END, StateGraph
from ml.agent.graph.nodes import (
    fast_answer_node,
    flash_memories_node,
    graph_mode_node,
    research_answer_node,
    research_observer_node,
    research_react_node,
    research_tool_call_node,
    thinking_planner_node,
)
from ml.agent.graph.state import GraphState, NextAction
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import RequestPayload, Tag
from ml.utils.tag_validation import define_tag
from ml.utils.voice_validation import form_final_report, validate_voice
from ollama import ChatResponse

logger: logging.Logger = logging.getLogger(__name__)


def _extract_pipeline_mode(state: GraphState) -> str:
    return state.payload.mode.value


def _extract_research_route(state: GraphState) -> str:
    if state.final_prompt is not None:
        return NextAction.FINISH.value
    return state.next_action.value


def create_pipeline(client: ReasoningModelClient) -> StateGraph:
    """Create the LangGraph pipeline."""

    # Create graph
    workflow: StateGraph = StateGraph(GraphState)

    # Nodes
    workflow.add_node("Mode Decider", graph_mode_node)
    # Not implemented yet
    workflow.add_node("Flash Memories", flash_memories_node)
    workflow.add_node("Thinking planner", partial(thinking_planner_node, client=client))
    workflow.add_node("Research react", partial(research_react_node, client=client))
    workflow.add_node("Research tool call", partial(research_tool_call_node, client=client))
    workflow.add_node("Research observer", partial(research_observer_node, client=client))
    workflow.add_node("Research answer", research_answer_node)
    workflow.add_node(
        "Fast answer", fast_answer_node
    )  # not passing model cuz forming a final prompt

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
            "research": "Research react",
        },
    )

    # # edges

    # Fast
    workflow.add_edge("Flash Memories", "Fast answer")
    workflow.add_edge("Fast answer", END)

    # Research
    workflow.add_conditional_edges(
        "Research react",
        _extract_research_route,
        {
            NextAction.THINK.value: "Research react",
            NextAction.REQUEST_TOOL.value: "Research tool call",
            NextAction.ANSWER.value: "Research answer",
            NextAction.FINISH.value: "Research answer",
        },
    )
    workflow.add_edge("Research tool call", "Research observer")
    workflow.add_conditional_edges(
        "Research observer",
        _extract_research_route,
        {
            NextAction.THINK.value: "Research react",
            NextAction.ANSWER.value: "Research answer",
            NextAction.FINISH.value: "Research answer",
        },
    )
    workflow.add_edge("Research answer", END)

    app: StateGraph = workflow.compile()

    return app


def run_pipeline(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
    # Create Reasoning model client
    client: ReasoningModelClient = ReasoningModelClient()

    # validate user request if voice
    if payload.is_voice:
        voice_is_valid: bool = validate_voice(
            voice_decoding=payload.messages.last_message_as_history(),
            reasoning_client=client,
        )
        if not voice_is_valid:
            logger.warning(
                "Voice validation failed. Returning fallback stream. Conversation: %s",
                payload.messages.model_dump_string(),
            )
            if not payload.tag:
                error_message: str = (
                    "Voice validation failed for a conversation without a tag."
                )
                logger.error(error_message)
                raise RuntimeError(error_message)
            logger.info("Returning fallback stream with tag %s", payload.tag.value)
            return form_final_report(reasoning_client=client), payload.tag

    # FUTURE: validate tag if tag is empty
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

    raw_result: dict[str, Any] = app.invoke(state)
    try:
        result: GraphState = GraphState.model_validate(raw_result)
    except:
        RuntimeError("GraphState parse Failed")

    logging.debug(
        "Started final prompt generation with payload: \n%s",
        result.final_prompt.model_dump_json(ensure_ascii=False, indent=2),
    )

    return client.stream(result.final_prompt), payload.tag
