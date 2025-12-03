from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import GraphState, PlannedToolCall, ToolCall
from ml.domain.workflow.agent.tools import BaseTool
from ml.domain.workflow.agent.tools.tool_registry import get_tool_registry

from .prompt import get_research_reason_prompt
from .schema import ResearchPlan


async def research_reason(state: GraphState) -> GraphState:
    client = ReasoningModelClient.instance()
    available_tools: dict[str, BaseTool] = get_tool_registry()

    prompt = get_research_reason_prompt(
        chat=state.chat,
        profile=state.user,
        available_tools=available_tools,
        evidence_list=state.evidence_list,
    )

    result: ResearchPlan = await client.call_structured(messages=prompt, output_schema=ResearchPlan)

    state.planned_tool_call = PlannedToolCall(
        thought=result.thought,
        chosen_tool=result.chosen_tool,
        tool_args=result.tool_args,
    )
    state.pending_tool_call = ToolCall(name=result.chosen_tool, arguments=result.tool_args)
    state.tool_call_history.append(state.pending_tool_call)
    state.last_executed_tool = None

    return state
