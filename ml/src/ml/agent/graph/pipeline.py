import asyncio
import logging
from collections.abc import Iterator
from functools import partial
from typing import Any

from langgraph.graph import END, StateGraph
from ml.agent.graph.nodes import (
    fast_answer_node,
    flash_memories_node,
    graph_mode_node,
    research_observer_node,
    research_react_node,
    research_tool_call_node,
    thinking_planner_node,
)
from ml.agent.graph.state import GraphState, NextAction
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import RequestPayload, Tag
from ml.utils.graph_logger import GraphLogClient, get_backend_url
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
    workflow.add_node(
        "Research tool call", partial(research_tool_call_node, client=client)
    )
    workflow.add_node(
        "Research observer", partial(research_observer_node, client=client)
    )
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
            NextAction.FINISH.value: "Fast answer",
        },
    )
    workflow.add_edge("Research tool call", "Research observer")
    workflow.add_conditional_edges(
        "Research observer",
        _extract_research_route,
        {
            NextAction.THINK.value: "Research react",
            NextAction.FINISH.value: "Fast answer",
        },
    )

    app: StateGraph = workflow.compile()

    return app


def run_pipeline(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
    # Create Reasoning model client
    client: ReasoningModelClient = ReasoningModelClient()

    # Инициализация GraphLogClient если есть answer_id
    graph_log_client: GraphLogClient | None = None
    loop = None
    if payload.answer_id:
        try:
            backend_url = get_backend_url()
            graph_log_client = GraphLogClient(
                backend_url=backend_url, chat_id=payload.chat_id
            )
            # Подключаемся к WebSocket (синхронный вызов async функции)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            connected = loop.run_until_complete(graph_log_client.connect())
            if not connected:
                logger.warning("Не удалось подключиться к WebSocket для graph_log")
                graph_log_client = None
        except Exception as e:
            logger.warning(f"Ошибка инициализации GraphLogClient: {e}")
            graph_log_client = None

    # validate user request if voice
    if payload.is_voice:
        if not validate_voice(
            voice_decoding=payload.messages.last_message_as_history(),
            reasoning_client=client,
        ):
            if graph_log_client and loop:
                try:
                    loop.run_until_complete(graph_log_client.close())
                except Exception:
                    pass
            return form_final_report(reasoning_client=client)

    # FUTURE: validate tag if tag is empty
    if not payload.tag:
        logger.info("Tag not found. Starting tag definition")
        payload.tag = define_tag(
            last_message=payload.messages.last_message_as_history(),
            reasoning_client=client,
        )
        logger.info("Defined a tag: %s", payload.tag.value)

    # Create Graph
    app: StateGraph = create_pipeline(client)

    # Create initial state with graph_log_client and event loop
    state: GraphState = GraphState(
        payload=payload,
        graph_log_client=graph_log_client,
        graph_log_loop=loop if graph_log_client else None,
    )

    try:
        raw_result: dict[str, Any] = app.invoke(state)
        try:
            result: GraphState = GraphState.model_validate(raw_result)
        except:
            RuntimeError("GraphState parse Failed")

        logging.debug(
            "Started final prompt generation with payload: \n%s",
            result.final_prompt.model_dump_json(ensure_ascii=False, indent=2),
        )
    finally:
        # Закрываем WebSocket соединение
        if graph_log_client and loop:
            try:
                loop.run_until_complete(graph_log_client.close())
            except Exception as e:
                logger.warning(f"Ошибка закрытия GraphLogClient: {e}")

    return client.stream(result.final_prompt), payload.tag
