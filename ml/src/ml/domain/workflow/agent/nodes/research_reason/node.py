import logging

from ml.api.external import send_graph_log
from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import GraphState, PlannedToolCall, ToolCall
from ml.domain.models.graph_log import PicsTags
from ml.domain.workflow.agent.tools import BaseTool
from ml.domain.workflow.agent.tools.tool_registry import get_tool_registry

from .prompt import get_research_reason_prompt
from .schema import ResearchPlan


logger = logging.getLogger(__name__)


async def research_reason(state: GraphState) -> GraphState:
    logger.info("Entering research_reason node")

    answer_id = state.chat.last_user_message_id()

    await send_graph_log(
        chat_id=state.chat_id, tag=PicsTags.Think, message="Думаю", answer_id=answer_id
    )

    client = ReasoningModelClient.instance()
    available_tools: dict[str, BaseTool] = get_tool_registry()

    prompt = get_research_reason_prompt(
        chat=state.chat,
        profile=state.user,
        available_tools=available_tools,
        evidence_list=state.evidence_list,
    )

    result: ResearchPlan = await client.call_structured(messages=prompt, output_schema=ResearchPlan)

    tool_arguments = dict(result.tool_args)
    if result.chosen_tool == "web_search":
        tool_arguments.update({"chat_id": state.chat_id, "answer_id": answer_id})

    state.planned_tool_call = PlannedToolCall(
        thought=result.thought,
        chosen_tool=result.chosen_tool,
        tool_args=tool_arguments,
    )
    state.pending_tool_call = ToolCall(name=result.chosen_tool, arguments=tool_arguments)
    state.tool_call_history.append(state.pending_tool_call)
    state.last_executed_tool = None

    return state
