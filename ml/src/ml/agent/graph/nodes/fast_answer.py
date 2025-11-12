from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.agent.prompts.fast_answer_prompt import PROMPT as FAST_ANSWER_PROMPT
 

def fast_answer_node(state: GraphState, _client: _ReasoningModelClient) -> GraphState:
    """Generate fast answer prompt without tools."""

    state.record_event(
        "node.enter",
        node="fast_answer",
        message_history=len(state.messages),
    )

    # Prepare messages with conversation history
    messages = [{"role": "system", "content": FAST_ANSWER_PROMPT}]

    # Add conversation history
    for msg in state.messages:
        messages.append({
            "role": msg.role.value,
            "content": msg.content
        })

    state.final_prompt_messages = messages
    state.stream_messages = messages
    state.final_answer = None

    state.record_event(
        "fast_answer.prompt_prepared",
        node="fast_answer",
        message_count=len(messages),
    )

    return state
