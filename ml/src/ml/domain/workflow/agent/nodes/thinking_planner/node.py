import logging

from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import GraphState, PlannedToolCall, ToolCall
from ml.domain.workflow.agent.tools.tool_registry import get_tool

from .prompt import get_thinking_plan_prompt
from .schema import ThinkingPlan


logger = logging.getLogger(__name__)


async def thinking_planner(state: GraphState) -> GraphState:
    logger.info("Entering thinking_planner node")

    prompt = get_thinking_plan_prompt(chat=state.chat, profile=state.user)

    client = ReasoningModelClient.instance()
    plan: ThinkingPlan = await client.call_structured(messages=prompt, output_schema=ThinkingPlan)

    web_search_tool = get_tool("web_search")
    if web_search_tool is None:
        raise RuntimeError("Web search tool is not registered")

    tool_arguments = {"query": plan.query}

    state.planned_tool_call = PlannedToolCall(
        thought=plan.thought, chosen_tool=web_search_tool.name, tool_args=tool_arguments
    )
    state.pending_tool_call = ToolCall(name=web_search_tool.name, arguments=tool_arguments)
    state.tool_call_history.append(state.pending_tool_call)

    state.last_executed_tool = None
    state.last_tool_result = None

    return state
