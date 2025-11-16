"""LLM command node that finalizes research tool calls."""

import json
import logging
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from ml.agent.graph.constants import (
    FORCE_FINALIZE_METADATA_KEY,
    STOP_REASON_KEY,
    STOP_TOOL_NAME,
)
from ml.agent.graph.nodes.tooling import select_primary_input
from ml.agent.graph.state import GraphState, NextAction, ResearchToolRequest
from ml.agent.prompts import get_research_tool_prompt
from ml.agent.tools.registry import get_tool_registry
from ml.api.ollama_calls import ReasoningModelClient

logger: logging.Logger = logging.getLogger(__name__)


class ToolCommandResponse(BaseModel):
    """Structured response returned by the tool command model."""

    action: Literal["call_tool", "finalize_answer"]
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    justification: str = Field(default="")


def _extract_json_blob(response_text: str) -> str:
    """Extract the JSON substring from a model response."""

    fence_index = response_text.find("```")
    if fence_index != -1:
        closing_index = response_text.find("```", fence_index + 3)
        if closing_index != -1:
            candidate = response_text[fence_index + 3 : closing_index]
            if candidate.startswith("json"):
                return candidate[4:]
            return candidate
    start_index = response_text.find("{")
    end_index = response_text.rfind("}")
    if start_index != -1 and end_index != -1 and end_index >= start_index:
        return response_text[start_index : end_index + 1]
    return response_text


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


def _finalize_from_justification(state: GraphState, justification: str) -> GraphState:
    if state.turn_history:
        last_turn = state.turn_history[-1]
        last_turn.reasoning_summary = justification
        last_turn.request = None
    state.active_tool_request = None
    state.latest_reasoning_text = justification
    state.next_action = NextAction.ANSWER
    return state


def tool_command_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Research tool command node")
    pending_request = state.active_tool_request
    if pending_request is None:
        error_message = "Active tool request is missing for tool command node"
        logger.error(error_message)
        raise ValueError(error_message)

    metadata = pending_request.metadata or {}
    force_finalize = metadata.get(FORCE_FINALIZE_METADATA_KEY)
    if force_finalize or pending_request.tool_name == STOP_TOOL_NAME:
        stop_reason = metadata.get(STOP_REASON_KEY)
        justification = stop_reason or (
            "Достигнут лимит исследовательских итераций. Закрываем расследование."
        )
        logger.info(
            "Tool command received forced finalize directive from %s", pending_request.tool_name
        )
        return _finalize_from_justification(state, justification)

    comparison_note = pending_request.metadata.get("comparison_text") if pending_request.metadata else None
    prompt = get_research_tool_prompt(
        conversation=state.payload.messages,
        turn_history=state.turn_history,
        pending_request=pending_request,
        comparison_note=comparison_note,
        profile=state.payload.profile,
    )

    response_text = client.call(messages=prompt)
    logger.debug("Tool command raw response: %s", response_text)

    payload_text = _extract_json_blob(response_text)
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        logger.exception("Failed to parse tool command JSON: %s", exc)
        raise ValueError("Tool command response is not valid JSON") from exc

    try:
        command = ToolCommandResponse.model_validate(payload)
    except ValidationError as exc:
        logger.exception("Tool command response failed validation: %s", exc)
        raise ValueError("Tool command response is malformed") from exc

    normalized_arguments = _normalize_arguments(command.arguments)
    registry = get_tool_registry()

    if command.action == "finalize_answer":
        logger.info("Tool command requested to finalize the research answer")
        return _finalize_from_justification(state, command.justification)

    tool_name = command.tool_name
    if tool_name is None:
        error_message = "Tool command is missing tool_name for call_tool action"
        logger.error(error_message)
        raise ValueError(error_message)

    if tool_name not in registry:
        error_message = f"Requested tool '{tool_name}' is not registered"
        logger.error(error_message)
        raise ValueError(error_message)

    metadata = dict(pending_request.metadata)
    metadata["arguments"] = dict(normalized_arguments)

    finalized_request = ResearchToolRequest(
        tool_name=tool_name,
        input_text=select_primary_input(normalized_arguments),
        arguments=dict(normalized_arguments),
        metadata=metadata,
    )

    state.active_tool_request = finalized_request
    state.latest_reasoning_text = command.justification
    if state.turn_history:
        state.turn_history[-1].request = finalized_request
        state.turn_history[-1].reasoning_summary = command.justification
    logger.info("Tool command finalized request for tool %s", tool_name)
    state.next_action = NextAction.REQUEST_TOOL

    return state
