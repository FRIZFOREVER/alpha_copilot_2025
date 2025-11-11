from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.configs.message import Role, Message
from ml.agent.prompts.fast_answer_prompt import PROMPT as FAST_ANSWER_PROMPT


def fast_answer_node(state: GraphState, client: _ReasoningModelClient) -> GraphState:
    """Generate fast answer without tools."""
    
    # Prepare messages with conversation history
    messages = [{"role": "system", "content": FAST_ANSWER_PROMPT}]
    
    # Add conversation history
    for msg in state.messages:
        messages.append({
            "role": msg.role.value,
            "content": msg.content
        })
    
    # Get answer
    try:
        response = client.call(messages=messages)
        state.final_answer = response.content
    except Exception as e:
        state.final_answer = f"Извините, произошла ошибка при генерации ответа: {str(e)}"
    
    return state
