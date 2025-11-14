import logging
from typing import Any, Dict, Iterator

from langgraph.graph import END, StateGraph
from ollama import ChatResponse

from ml.agent.graph.nodes import (
    fast_answer_node,
    flash_memories_node,
    graph_mode_node,
    research_react_node,
    thinking_planner_node,
)
from ml.agent.graph.state import GraphState
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import RequestPayload, Tag
from ml.utils.tag_validation import define_tag
from ml.utils.voice_validation import form_final_report, validate_voice

logger = logging.getLogger(__name__)


def _extract_pipeline_mode(state: GraphState) -> str:
    return state.payload.mode.value


def create_pipeline(client: ReasoningModelClient) -> StateGraph:
    """Create the LangGraph pipeline."""

    # Create graph
    workflow: StateGraph = StateGraph(GraphState)

    # Nodes
    workflow.add_node("Mode Decider", graph_mode_node)
    # Not implemented yet
    workflow.add_node("Flash Memories", flash_memories_node)
    workflow.add_node("Thinking planner", thinking_planner_node, client=client)
    workflow.add_node("Research react", research_react_node, client=client)
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

    app: StateGraph = workflow.compile()

    return app


def run_pipeline(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
    # Create Reasoning model client
    client: ReasoningModelClient = ReasoningModelClient()

    # validate user request if voice
    if payload.is_voice:
        if not validate_voice(
            voice_decoding=payload.messages.last_message_as_history(),
            reasoning_client=client,
        ):
            return form_final_report(reasoning_client=client)

    # FUTURE: validate tag if tag is empty
    if not payload.tag:
        logger.info("Tag not found. Starting tag definition")
        payload.tag = define_tag(
            last_message=payload.messages.last_message_as_history(),
            reasoning_client=client
        )
        logger.info("Defined a tag: %s", payload.tag.value)
    
    # Create Graph
    app: StateGraph = create_pipeline(client)

    # Create initial state
    state: GraphState = GraphState(payload=payload)

    raw_result: Dict[str, Any] = app.invoke(state)
    result: GraphState = GraphState.model_validate(raw_result)
    logging.debug(
        "Started final prompt generation with payload: \n%s",
        result.final_prompt.model_dump_json(ensure_ascii=False, indent=2),
    )
    return client.stream(result.final_prompt), payload.tag
