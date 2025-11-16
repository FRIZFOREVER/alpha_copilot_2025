"""Minimal thinking planner node that only relies on the latest user request."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from ml.agent.graph.state import GraphState, NextAction, PlannerToolExecution
from ml.agent.prompts import ThinkingPlannerAction, get_thinking_planner_prompt
from ml.agent.tools.base import BaseTool
from ml.agent.tools.registry import get_tool_registry
from ml.api.graph_logging import log_think
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


def thinking_planner_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Thinking planner node")
    log_think(state, "Думаю")
    user_request = _latest_user_request(state.payload.messages)
    if not user_request:
        logger.warning("Planner skipped: no user request found")
        state.next_action = NextAction.ANSWER
        return state

    registry = get_tool_registry()
    available_tools: Sequence[BaseTool] = list(registry.values())

    executions: list[PlannerToolExecution] = []
    last_used_tool: str | None = None
    collected_evidence: list[str] = []

    for iteration in range(2):
        logger.info("Planner iteration %s", iteration + 1)
        prompt = get_thinking_planner_prompt(
            profile=state.payload.profile,
            messages=state.payload.messages,
            available_tools=available_tools,
        )
        action: ThinkingPlannerAction = client.call_structured(prompt, ThinkingPlannerAction)
        tool_name = action.tool_name
        if not tool_name:
            logger.info("Planner returned empty tool name, stopping early")
            break

        tool = registry.get(tool_name)
        if tool is None:
            logger.warning("Requested tool '%s' is not registered", tool_name)
            break

        if last_used_tool == tool_name:
            logger.info("Skipping duplicate tool '%s' to avoid re-execution", tool_name)
            break

        result = tool.execute(**action.arguments)
        payload = result.data if result.success else result.error
        preview = str(payload) if payload is not None else ""
        executions.append(
            PlannerToolExecution(
                tool_name=tool_name,
                arguments=action.arguments,
                success=result.success,
                output_preview=preview,
            )
        )
        last_used_tool = tool_name

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
    return state
