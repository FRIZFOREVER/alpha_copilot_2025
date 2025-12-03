from ml.domain.models import Evidence, GraphState


def research_observer(state: GraphState) -> GraphState:
    tool_call = state.pending_tool_call
    if tool_call is None:
        raise RuntimeError("No tool call available to observe")

    result = state.last_tool_result
    if result is None:
        raise RuntimeError("Missing tool result for observation step")

    observation = Evidence(tool_name=tool_call.tool_name, summary=str(result.data), source=result)
    state.evidence_list.append(observation)

    state.pending_tool_call = None
    state.last_tool_result = None

    return state
