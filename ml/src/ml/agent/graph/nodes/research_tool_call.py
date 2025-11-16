"""Tool execution node for research workflow."""

import asyncio
import logging
from random import shuffle
from typing import Any

from ml.agent.graph.state import GraphState, NextAction, ResearchObservation
from ml.agent.tools.base import ToolResult
from ml.agent.tools.registry import get_tool

logger = logging.getLogger(__name__)


def research_tool_call_node(state: GraphState, client: Any) -> GraphState:
    request = state.active_tool_request

    tool_result: ToolResult

    comparison_text = request.metadata.get("comparison_text", "")
    tool = get_tool("web_search")
    tool_result = tool.execute(query=request.input_text)

    payload: dict[str, Any] = {}
    payload = dict(tool_result.data)

    results = payload.get("results")

    shuffled_results = list(results)
    shuffle(shuffled_results)
    payload["results"] = shuffled_results
    payload["count"] = len(shuffled_results)

    metadata: dict[str, Any] = {
        "success": tool_result.success,
        "payload": payload,
    }

    if tool_result.error:
        metadata["error"] = tool_result.error

    if comparison_text:
        metadata["comparison_text"] = comparison_text

    content = ""
    if tool_result.success and request:
        content = request.input_text
    elif tool_result.error:
        content = tool_result.error

    observation = ResearchObservation(
        tool_name="web_search",
        content=content,
        metadata=metadata,
    )

    if state.turn_history:
        state.turn_history[-1].observation = observation

    state.active_observation = observation
    state.active_tool_request = None
    state.next_action = NextAction.AWAIT_OBSERVATION

    # Логирование вызова инструмента
    if (
        state.graph_log_client
        and state.payload.answer_id
        and state.payload.tag
        and state.graph_log_loop
    ):
        try:
            tool_info = f"Tool: {request.tool_name}, Query: {request.input_text[:200]}"
            # Используем event loop для отправки лога
            state.graph_log_loop.run_until_complete(
                state.graph_log_client.send_log(
                    tag=state.payload.tag.value,
                    answer_id=state.payload.answer_id,
                    message=f"Research Tool Call - {tool_info}",
                )
            )
        except Exception as e:
            logger.warning(f"Ошибка отправки graph_log: {e}")

    return state
