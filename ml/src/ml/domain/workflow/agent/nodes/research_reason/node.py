from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import ChatHistory, GraphState
from ml.domain.workflow.agent.tools import BaseTool
from ml.domain.workflow.agent.tools.tool_registry import get_tool_registry

from .prompt import get_research_reason_prompt


async def research_reason(state: GraphState) -> GraphState:
    client = ReasoningModelClient.instance()
    available_tools: dict[str, BaseTool] = get_tool_registry()

    prompt: ChatHistory = get_research_reason_prompt(
        chat=state.chat,
        profile=state.user,
        available_tools=available_tools,
    )

    result = await client.call(messages=prompt)

    return state
