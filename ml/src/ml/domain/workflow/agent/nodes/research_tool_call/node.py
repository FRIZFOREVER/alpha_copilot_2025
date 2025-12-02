from ml.domain.models import GraphState
from ml.domain.workflow.agent.tools.tool_registry import get_tool


def research_tool_call(state: GraphState) -> GraphState:
    tool_call = state.pending_tool_call
    if tool_call is None:
        raise RuntimeError("No pending tool call to execute")

    tool = get_tool(tool_call.tool_name)
    if tool is None:
        raise RuntimeError(f"Tool '{tool_call.tool_name}' is not registered")

    state.last_tool_result = tool.execute(**tool_call.arguments)

    return state
