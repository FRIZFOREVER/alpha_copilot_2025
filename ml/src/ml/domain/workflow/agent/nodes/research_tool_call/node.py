import logging

from ml.domain.models import GraphState, ToolResult
from ml.domain.workflow.agent.tools.final_answer.tool import FinalAnswerTool
from ml.domain.workflow.agent.tools.tool_registry import get_tool

logger = logging.getLogger(__name__)


async def research_tool_call(state: GraphState) -> GraphState:
    logger.info("Entering research_tool_call node")

    planned_call = state.pending_tool_call
    if planned_call is None:
        raise RuntimeError("No planned tool call found")

    tool = get_tool(planned_call.tool_name)
    if tool is None:
        raise RuntimeError(f"Tool '{planned_call.tool_name}' is not registered")

    execution_arguments = dict(planned_call.arguments)
    final_answer_name = FinalAnswerTool().name
    if tool.name == final_answer_name:
        execution_arguments.update(
            {
                "chat": state.chat,
                "profile": state.user,
                "evidence": state.evidence_list,
            }
        )

    try:
        result: ToolResult = await tool.execute(**execution_arguments)
    except Exception as exc:
        logger.exception("Tool execution failed for %s", planned_call.tool_name)
        result = ToolResult(success=False, data={}, error=str(exc))
    planned_call.result = result
    state.last_tool_result = result
    state.last_executed_tool = tool.name

    if tool.name == final_answer_name:
        if not isinstance(result.data, dict):
            raise ValueError("Final answer tool result must contain final prompt data")
        if "final_prompt" not in result.data:
            raise ValueError("Final answer tool result missing final prompt")
        final_prompt = result.data["final_prompt"]
        if not isinstance(final_prompt, type(state.chat)):
            raise ValueError("Final prompt missing or invalid in final answer tool result")
        state.final_prompt = final_prompt
        state.pending_tool_call = None

    return state
