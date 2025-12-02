from ml.domain.models import GraphState, PlannedToolCall


async def research_reason(state: GraphState) -> GraphState:
    if state.pending_tool_call is not None:
        return state

    latest_request = state.chat.last_message()

    if len(state.observations) < 2:
        state.pending_tool_call = PlannedToolCall(
            tool_name="web_search",
            arguments={
                "query": latest_request.content,
                "round": len(state.observations) + 1,
            },
        )

    return state
