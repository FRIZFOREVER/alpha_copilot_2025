from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.agent.prompts.fast_answer_prompt import PROMPT as FAST_ANSWER_PROMPT


def fast_answer_node(state: GraphState, _client: _ReasoningModelClient) -> GraphState:
    """Generate fast answer prompt without tools."""

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

    return state
