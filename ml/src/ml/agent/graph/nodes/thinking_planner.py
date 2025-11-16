"""Minimal thinking planner node that only relies on the latest user request."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from ml.agent.graph.state import GraphState, NextAction, PlannerToolExecution
from ml.agent.prompts import ThinkingPlannerAction, get_thinking_planner_prompt
from ml.agent.tools.base import BaseTool, ToolResult
from ml.agent.tools.registry import get_tool_registry
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory, Role

logger: logging.Logger = logging.getLogger(__name__)


def _latest_user_request(conversation: ChatHistory) -> str:
    try:
        messages = conversation.messages
    except AttributeError:
        logger.exception("Conversation history is missing the messages attribute")
        raise

    for message in reversed(messages):
        if message.role == Role.user:
            return message.content
    return ""


def _preview_payload(result: ToolResult) -> str:
    payload = result.data if result.success else result.error
    if payload is None:
        return ""
    text = str(payload)
    if len(text) > 600:
        return text[:600]
    return text


def _execute_tool(tool: BaseTool, arguments: dict[str, str]) -> ToolResult:
    return tool.execute(**arguments)


def _build_prompt(user_request: str, tools: Sequence[BaseTool]) -> ChatHistory:
    return get_thinking_planner_prompt(user_request=user_request, available_tools=tools)


def thinking_planner_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Thinking planner node")
    user_request = _latest_user_request(state.payload.messages)
    if not user_request:
        logger.warning("Planner skipped: no user request found")
        state.next_action = NextAction.ANSWER
        return state

    registry = get_tool_registry()
    available_tools: Sequence[BaseTool] = list(registry.values())

    executions: list[PlannerToolExecution] = []
    collected_evidence: list[str] = []

    for iteration in range(2):
        logger.info("Planner iteration %s", iteration + 1)
        prompt = _build_prompt(user_request, available_tools)
        action: ThinkingPlannerAction = client.call_structured(prompt, ThinkingPlannerAction)
        tool_name = action.tool_name
        if not tool_name:
            logger.info("Planner returned empty tool name, stopping early")
            break

        tool = registry.get(tool_name)
        if tool is None:
            logger.warning("Requested tool '%s' is not registered", tool_name)
            break

        result = _execute_tool(tool, action.arguments)
        preview = _preview_payload(result)
        executions.append(
            PlannerToolExecution(
                tool_name=tool_name,
                arguments=action.arguments,
                success=result.success,
                output_preview=preview,
            )
        )

        if preview:
            collected_evidence.append(preview)

        if not result.success:
            logger.warning("Tool '%s' failed, stopping planner loop", tool_name)
            break

    if collected_evidence:
        state.thinking_evidence.extend(collected_evidence)
        state.final_answer_evidence.extend(collected_evidence)

    state.thinking_tool_executions = executions
    state.thinking_plan_summary = None
    state.thinking_plan_steps = []
    state.final_answer_draft = None
    state.next_action = NextAction.ANSWER
    return state
