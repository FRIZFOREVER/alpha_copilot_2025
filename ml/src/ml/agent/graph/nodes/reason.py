"""Reasoning node responsible for preparing tool calls in the research workflow."""

import logging
from typing import Any

from ml.agent.graph.state import (
    GraphState,
    NextAction,
    ResearchToolRequest,
    ResearchTurn,
)
from ml.agent.prompts import get_research_reason_prompt
from ml.agent.tools.registry import get_tool_registry
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory

MAX_REASONING_LOOPS = 6

logger: logging.Logger = logging.getLogger(__name__)

_REASON_HEADER = "reason:"
_TOOL_HEADER = "suggested tool:"
_PLAN_HEADER = "call plan:"
_KNOWN_INPUT_KEYS: tuple[str, ...] = (
    "query",
    "input",
    "input_text",
    "request",
    "prompt",
)


def _split_template_sections(raw: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {
        _REASON_HEADER: [],
        _TOOL_HEADER: [],
        _PLAN_HEADER: [],
    }
    current: str | None = None
    for line in raw.split("\n"):
        lowered = line.lower()
        if lowered.startswith(_REASON_HEADER):
            current = _REASON_HEADER
            sections[current] = [line[len(_REASON_HEADER) :]]
            continue
        if lowered.startswith(_TOOL_HEADER):
            current = _TOOL_HEADER
            sections[current] = [line[len(_TOOL_HEADER) :]]
            continue
        if lowered.startswith(_PLAN_HEADER):
            current = _PLAN_HEADER
            sections[current] = [line[len(_PLAN_HEADER) :]]
            continue
        if current is None:
            continue
        sections[current].append(line)
    return {key: "\n".join(value) for key, value in sections.items()}


def _extract_tool_name(section_text: str) -> str:
    for line in section_text.split("\n"):
        if line == "":
            continue
        return line
    error_message = "Reasoning response did not include a tool name"
    logger.error(error_message)
    raise ValueError(error_message)


def _parse_call_plan(section_text: str) -> tuple[str | None, dict[str, str]]:
    objective: str | None = None
    arguments: dict[str, str] = {}
    for line in section_text.split("\n"):
        if not line:
            continue
        lowered = line.lower()
        if lowered.startswith("objective:"):
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    objective = parts[1]
                    continue
        if ":" not in line:
            continue
        parts = line.split(":", 1)
        if len(parts) != 2:
            continue
        key = parts[0]
        value = parts[1]
        if key:
            arguments[key] = value
    return objective, arguments


def _select_primary_input(arguments: dict[str, str]) -> str:
    for key in _KNOWN_INPUT_KEYS:
        candidate = arguments.get(key)
        if candidate is None:
            continue
        if candidate == "":
            continue
        return candidate
    return ""


def reason_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Research reason node")
    if state.loop_counter >= MAX_REASONING_LOOPS:
        error_message = "Reasoning loop limit exceeded before scheduling a tool call"
        logger.error(error_message)
        raise RuntimeError(error_message)

    available_tools = list(get_tool_registry().values())
    prompt: ChatHistory = get_research_reason_prompt(
        profile=state.payload.profile,
        conversation=state.payload.messages,
        turn_history=state.turn_history,
        latest_reasoning=state.latest_reasoning_text,
        available_tools=available_tools,
    )

    response_text = client.call(messages=prompt)
    sections = _split_template_sections(response_text)

    reason_section = sections.get(_REASON_HEADER, "")
    tool_section = sections.get(_TOOL_HEADER, "")
    plan_section = sections.get(_PLAN_HEADER, "")

    if reason_section == "" or tool_section == "" or plan_section == "":
        error_message = "Reasoning response template is incomplete"
        logger.error(error_message)
        raise ValueError(error_message)

    suggested_tool = _extract_tool_name(tool_section)
    objective, arguments = _parse_call_plan(plan_section)

    state.loop_counter = state.loop_counter + 1
    state.latest_reasoning_text = reason_section
    state.suggested_tool_name = suggested_tool
    state.suggested_tool_args = dict(arguments)
    state.suggested_objective = objective

    metadata: dict[str, Any] = {"arguments": dict(arguments)}
    if objective is not None:
        metadata["objective"] = objective
    comparison_note = arguments.get("comparison_text")
    if comparison_note is not None:
        metadata["comparison_text"] = comparison_note

    tool_input = _select_primary_input(arguments)

    tool_request = ResearchToolRequest(
        tool_name=suggested_tool,
        input_text=tool_input,
        metadata=metadata,
    )

    turn = ResearchTurn(
        reasoning_summary=reason_section,
        request=tool_request,
    )

    state.active_tool_request = tool_request
    state.turn_history.append(turn)
    state.next_action = NextAction.REQUEST_TOOL

    logger.info("Reasoning summary ready, tool %s will be prepared", suggested_tool)
    return state
