"""Tool execution node for research workflow."""

import logging
from random import shuffle
from typing import Any

from ml.agent.graph.state import GraphState, NextAction, ResearchObservation, ResearchToolRequest
from ml.agent.tools.base import BaseTool, ToolResult
from ml.agent.tools.registry import get_tool

logger: logging.Logger = logging.getLogger(__name__)


def _validate_tool_arguments(request: ResearchToolRequest, tool: BaseTool) -> None:
    schema = tool.schema
    arguments = request.arguments
    if not arguments:
        error_message = f"Tool '{tool.name}' requires arguments"
        logger.error(error_message)
        raise ValueError(error_message)

    required = schema.get("required") if hasattr(schema, "get") else None
    properties = schema.get("properties") if hasattr(schema, "get") else None
    additional_allowed = schema.get("additionalProperties") if hasattr(schema, "get") else True

    if required:
        for field in required:
            value = arguments.get(field)
            if value is None:
                error_message = f"Missing required argument '{field}' for tool '{tool.name}'"
                logger.error(error_message)
                raise ValueError(error_message)
            if not isinstance(value, str):
                error_message = f"Argument '{field}' must be a string for tool '{tool.name}'"
                logger.error(error_message)
                raise ValueError(error_message)
            if value == "":
                error_message = f"Argument '{field}' cannot be empty for tool '{tool.name}'"
                logger.error(error_message)
                raise ValueError(error_message)

    if not additional_allowed and properties is not None:
        for key in arguments:
            if key not in properties:
                error_message = f"Unexpected argument '{key}' for tool '{tool.name}'"
                logger.error(error_message)
                raise ValueError(error_message)

    if properties:
        for key, descriptor in properties.items():
            if key not in arguments:
                continue
            expected_type = descriptor.get("type") if hasattr(descriptor, "get") else None
            if expected_type == "string" and not isinstance(arguments[key], str):
                error_message = f"Argument '{key}' must be a string for tool '{tool.name}'"
                logger.error(error_message)
                raise ValueError(error_message)


def _prepare_payload(result: ToolResult) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if isinstance(result.data, dict):
        payload = dict(result.data)
    elif result.data is not None:
        payload = {"data": result.data}

    results = payload.get("results") if hasattr(payload, "get") else None
    if results is not None:
        if not hasattr(results, "__iter__"):
            error_message = "Tool results payload must be iterable"
            logger.error(error_message)
            raise ValueError(error_message)
        shuffled_results = list(results)
        shuffle(shuffled_results)
        payload["results"] = shuffled_results
        payload["count"] = len(shuffled_results)
    return payload


def research_tool_call_node(state: GraphState, client: Any) -> GraphState:
    logger.info("Entered Research tool call node")
    request = state.active_tool_request
    if request is None:
        error_message = "Active tool request is missing for research tool call"
        logger.error(error_message)
        raise ValueError(error_message)

    tool = get_tool(request.tool_name)
    if tool is None:
        error_message = f"Requested tool '{request.tool_name}' is not registered"
        logger.error(error_message)
        raise ValueError(error_message)

    _validate_tool_arguments(request, tool)

    tool_result = tool.execute(**request.arguments)
    payload = _prepare_payload(tool_result)

    metadata: dict[str, Any] = dict(request.metadata)
    metadata["success"] = tool_result.success
    metadata["payload"] = payload
    if tool_result.error:
        metadata["error"] = tool_result.error

    content = request.input_text
    if not tool_result.success and tool_result.error:
        content = tool_result.error

    observation = ResearchObservation(
        tool_name=request.tool_name,
        content=content,
        metadata=metadata,
    )

    if state.turn_history:
        state.turn_history[-1].observation = observation

    state.active_observation = observation
    state.active_tool_request = None
    state.next_action = NextAction.AWAIT_OBSERVATION

    return state
