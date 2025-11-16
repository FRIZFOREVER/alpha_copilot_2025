"""Reasoning node responsible for planning the next research action."""

import logging

from ml.agent.graph.constants import STOP_TOOL_NAME
from ml.agent.graph.state import GraphState, NextAction, ResearchTurn
from ml.agent.prompts import get_research_reason_prompt
from ml.agent.tools.registry import get_tool_registry
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory

MAX_REASONING_LOOPS = 6

logger: logging.Logger = logging.getLogger(__name__)

_REASON_HEADER = "reason:"
_TOOL_HEADER = "suggested tool:"
_EXPECTED_INFO_HEADER = "expected information:"


def _split_template_sections(raw: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {
        _REASON_HEADER: [],
        _TOOL_HEADER: [],
        _EXPECTED_INFO_HEADER: [],
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
        if lowered.startswith(_EXPECTED_INFO_HEADER):
            current = _EXPECTED_INFO_HEADER
            sections[current] = [line[len(_EXPECTED_INFO_HEADER) :]]
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


def _prepare_forced_finalize(state: GraphState) -> GraphState:
    logger.warning("Reasoning loop limit reached, requesting finalization")
    summary = (
        "Достигнут лимит исследовательских итераций. Сформируй итоговый ответ без новых "
        "вызовов инструментов."
    )
    turn = ResearchTurn(reasoning_summary=summary)
    state.turn_history.append(turn)
    state.latest_reasoning_text = summary
    state.suggested_tool_name = STOP_TOOL_NAME
    state.suggested_objective = summary
    state.next_action = NextAction.REQUEST_TOOL
    return state


def reason_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Research reason node")
    if state.loop_counter >= MAX_REASONING_LOOPS:
        return _prepare_forced_finalize(state)

    available_tools = list(get_tool_registry().values())
    prompt: ChatHistory = get_research_reason_prompt(
        profile=state.payload.profile,
        conversation=state.payload.messages,
        turn_history=state.turn_history,
        evidence_snippets=state.final_answer_evidence,
        latest_reasoning=state.latest_reasoning_text,
        available_tools=available_tools,
    )

    response_text = client.call(messages=prompt)
    sections = _split_template_sections(response_text)

    reason_section = sections.get(_REASON_HEADER, "")
    tool_section = sections.get(_TOOL_HEADER, "")
    expectation_section = sections.get(_EXPECTED_INFO_HEADER, "")

    if reason_section == "" or tool_section == "" or expectation_section == "":
        error_message = "Reasoning response template is incomplete"
        logger.error(error_message)
        raise ValueError(error_message)

    suggested_tool = _extract_tool_name(tool_section)
    state.loop_counter = state.loop_counter + 1
    state.latest_reasoning_text = reason_section
    state.suggested_tool_name = suggested_tool
    state.suggested_objective = expectation_section

    turn = ResearchTurn(reasoning_summary=reason_section)
    state.turn_history.append(turn)
    state.next_action = NextAction.REQUEST_TOOL

    logger.info("Reasoning summary ready, suggested tool: %s", suggested_tool)
    return state
