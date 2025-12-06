import logging
from typing import Any

from ml.api.external import send_graph_log
from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import GraphState, PlannedToolCall, ToolCall
from ml.domain.models.graph_log import PicsTags
from ml.domain.workflow.agent.tools import BaseTool
from ml.domain.workflow.agent.tools.final_answer.tool import FinalAnswerTool
from ml.domain.workflow.agent.tools.tool_registry import get_tool_registry

from .prompt import get_thinking_plan_prompt
from .schema import ThinkingPlan


logger = logging.getLogger(__name__)


async def thinking_planner(state: GraphState) -> GraphState:
    logger.info("Entering thinking_planner node")

    answer_id = state.chat.last_user_message_id()

    await send_graph_log(
        chat_id=state.chat_id, tag=PicsTags.Think, message="Думаю", answer_id=answer_id
    )

    available_tools: dict[str, BaseTool] = get_tool_registry()
    if not available_tools:
        raise RuntimeError("No tools are registered for thinking planner")

    remaining_steps = max(0, 3 - len(state.tool_call_history))

    chosen_tool_name: str
    tool_arguments: dict[str, Any]
    thought: str

    if state.written_file_url is not None:
        final_tool_name = FinalAnswerTool().name
        final_tool = available_tools.get(final_tool_name)
        if final_tool is None:
            raise RuntimeError("Final answer tool is not registered")
        chosen_tool_name = final_tool.name
        thought = "Файл создан, формирую итоговый ответ."
        tool_arguments = {
            "chat": state.chat,
            "profile": state.user,
            "evidence": state.evidence_list,
        }
    elif remaining_steps == 0:
        final_tool_name = FinalAnswerTool().name
        final_tool = available_tools.get(final_tool_name)
        if final_tool is None:
            raise RuntimeError("Final answer tool is not registered")
        chosen_tool_name = final_tool.name
        thought = "Достигнут лимит вызовов инструментов, формирую итоговый ответ."
        tool_arguments = {
            "chat": state.chat,
            "profile": state.user,
            "evidence": state.evidence_list,
        }
    else:
        prompt = get_thinking_plan_prompt(
            chat=state.chat,
            profile=state.user,
            available_tools=available_tools,
            evidence_list=state.evidence_list,
            remaining_steps=remaining_steps,
        )

        client = ReasoningModelClient.instance()
        plan: ThinkingPlan = await client.call_structured(
            messages=prompt, output_schema=ThinkingPlan
        )

        chosen_tool_name = plan.chosen_tool
        thought = plan.thought
        tool_arguments = dict(plan.tool_args)

    chosen_tool = available_tools.get(chosen_tool_name)
    if chosen_tool is None:
        raise RuntimeError(f"Tool '{chosen_tool_name}' is not registered")

    if chosen_tool.name == "web_search":
        if "query" not in tool_arguments:
            raise KeyError("web_search tool requires 'query' argument")
        tool_arguments = {
            "query": tool_arguments["query"],
            "chat_id": state.chat_id,
            "answer_id": answer_id,
        }
    if chosen_tool.name == FinalAnswerTool().name:
        tool_arguments.update(
            {"chat": state.chat, "profile": state.user, "evidence": state.evidence_list}
        )

    state.planned_tool_call = PlannedToolCall(
        thought=thought, chosen_tool=chosen_tool.name, tool_args=tool_arguments
    )
    state.pending_tool_call = ToolCall(name=chosen_tool.name, arguments=tool_arguments)
    state.tool_call_history.append(state.pending_tool_call)

    state.last_executed_tool = None
    state.last_tool_result = None

    return state
