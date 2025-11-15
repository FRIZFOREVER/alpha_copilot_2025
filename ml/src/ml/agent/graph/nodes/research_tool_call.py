"""Tool execution node for research workflow."""

import logging
from random import shuffle
from typing import Any

from ml.agent.graph.state import GraphState, NextAction, ResearchObservation
from ml.agent.tools.base import ToolResult
from ml.agent.tools.registry import get_tool

logger: logging.Logger = logging.getLogger(__name__)


def research_tool_call_node(state: GraphState, client: Any) -> GraphState:
    request = state.active_tool_request

    if request is None:
        logger.error("Active tool request is missing for research tool call")
        raise ValueError("Active tool request is required")

    tool_result: ToolResult

    comparison_text = request.metadata.get("comparison_text", "")
    tool = get_tool("web_search")

    if tool is None:
        logger.error("Web search tool is not registered")
        raise ValueError("Web search tool is required")

    tool_result = tool.execute(query=request.input_text)

    payload: dict[str, Any] = {}
    payload = dict(tool_result.data)

    results = payload.get("results")

    if results is None or not hasattr(results, "__iter__"):
        logger.error("Web search tool returned invalid results payload")
        raise ValueError("Web search tool results must be iterable")

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

    return state
