"""Tool execution node for research workflow."""

from random import shuffle
from typing import Any, Dict

from ml.agent.graph.state import GraphState, NextAction, ResearchObservation
from ml.agent.tools.base import ToolResult
from ml.agent.tools.registry import get_tool


def research_tool_call_node(state: GraphState, client: Any) -> GraphState:
    request = state.active_tool_request

    tool_result: ToolResult

    comparison_text = request.metadata.get("comparison_text", "")
    tool = get_tool("web_search")
    tool_result = tool.execute(query=request.input_text)

    payload: Dict[str, Any] = {}
    payload = dict(tool_result.data)

    results = payload.get("results")
    
    shuffled_results = list(results)
    shuffle(shuffled_results)
    payload["results"] = shuffled_results
    payload["count"] = len(shuffled_results)

    metadata: Dict[str, Any] = {
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
