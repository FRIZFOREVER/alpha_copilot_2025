"""Tool selection and execution node for the research workflow."""

import logging
from random import shuffle
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from ml.agent.graph.nodes.tooling import select_primary_input
from ml.agent.graph.state import GraphState, NextAction, ResearchObservation, ResearchToolRequest
from ml.agent.prompts import get_research_tool_prompt
from ml.agent.tools.base import BaseTool, ToolResult
from ml.agent.tools.registry import get_tool, get_tool_registry
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory

logger: logging.Logger = logging.getLogger(__name__)


class ToolCallDecision(BaseModel):
    action: Literal["call_tool", "finalize_answer"]
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    justification: str = Field(default="")


def _normalize_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in arguments.items():
        if value is None:
            normalized[key] = ""
            continue
        if isinstance(value, str):
            normalized[key] = value
            continue
        normalized[key] = str(value)
    return normalized


def _validate_tool_arguments(arguments: dict[str, str], tool: BaseTool) -> None:
    schema = tool.schema
    if not arguments:
        error_message = f"Tool '{tool.name}' requires arguments"
        logger.error(error_message)
        raise ValueError(error_message)

    required = schema.get("required") if hasattr(schema, "get") else None
    properties = schema.get("properties") if hasattr(schema, "get") else None
    additional_allowed = schema.get("additionalProperties") if hasattr(schema, "get") else True

    if required:
        for field in required:
            try:
                value = arguments[field]
            except KeyError as exc:
                error_message = f"Missing required argument '{field}' for tool '{tool.name}'"
                logger.exception(error_message)
                raise ValueError(error_message) from exc
            if value is None:
                error_message = f"Argument '{field}' must not be None for tool '{tool.name}'"
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


def _finalize_from_justification(state: GraphState, justification: str) -> GraphState:
    note = justification or state.latest_reasoning_text or "Достаточно информации для ответа"
    state.latest_reasoning_text = note
    if state.turn_history:
        state.turn_history[-1].reasoning_summary = note
    state.active_observation = None
    state.next_action = NextAction.ANSWER
    return state


def _build_observation(
    request: ResearchToolRequest,
    tool_result: ToolResult,
) -> ResearchObservation:
    payload: dict[str, Any] = _prepare_payload(tool_result)
    metadata: dict[str, Any] = dict(request.metadata)
    metadata["success"] = tool_result.success
    metadata["payload"] = payload
    if tool_result.error:
        metadata["error"] = tool_result.error

    content = request.input_text
    if not tool_result.success and tool_result.error:
        content = tool_result.error

    return ResearchObservation(
        tool_name=request.tool_name,
        content=content,
        metadata=metadata,
    )


def research_tool_call_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Research tool call node")
    latest_reasoning: str | None = state.latest_reasoning_text

    if latest_reasoning is None:
        error_message = "Tool call node requires latest reasoning text"
        logger.error(error_message)
        raise ValueError(error_message)

    available_tools: list[BaseTool] = list(get_tool_registry().values())

    prompt: ChatHistory = get_research_tool_prompt(
        profile=state.payload.profile,
        conversation=state.payload.messages,
        latest_reasoning=latest_reasoning,
        evidence_snippets=state.final_answer_evidence,
        available_tools=available_tools,
    )

    try:
        decision = client.call_structured(messages=prompt, output_schema=ToolCallDecision)
    except ValidationError:
        logger.exception("Tool decision schema validation failed")
        raise
    except Exception:
        logger.exception("Failed to obtain tool decision")
        raise

    if decision.action == "finalize_answer":
        return _finalize_from_justification(state, decision.justification)

    tool_name: str | None = decision.tool_name
    if tool_name is None:
        error_message = "Structured decision is missing tool_name for call_tool action"
        logger.error(error_message)
        raise ValueError(error_message)

    tool: BaseTool | None = get_tool(tool_name)
    if tool is None:
        error_message = f"Requested tool '{tool_name}' is not registered"
        logger.error(error_message)
        raise ValueError(error_message)

    normalized_arguments = _normalize_arguments(decision.arguments)
    _validate_tool_arguments(normalized_arguments, tool)

    request_metadata: dict[str, Any] = {}
    if decision.justification:
        request_metadata["justification"] = decision.justification
    request = ResearchToolRequest(
        tool_name=tool_name,
        input_text=select_primary_input(normalized_arguments),
        arguments=dict(normalized_arguments),
        metadata=request_metadata,
    )

    tool_result = tool.execute(**request.arguments)
    observation = _build_observation(request, tool_result)

    if state.turn_history:
        turn = state.turn_history[-1]
        turn.request = request
        if decision.justification:
            turn.reasoning_summary = decision.justification

    state.active_observation = observation
    state.next_action = NextAction.OBSERVATION

    return state
