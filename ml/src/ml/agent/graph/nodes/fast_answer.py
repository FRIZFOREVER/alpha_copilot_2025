from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.configs.message import Role, Message
import os


def fast_answer_node(state: GraphState, client: _ReasoningModelClient) -> GraphState:
    """Generate fast answer without tools."""
    
    # Load fast answer prompt
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "prompts", "fast_answer_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        fast_answer_prompt = f.read()
    
    # Prepare messages with conversation history
    messages = [{"role": "system", "content": fast_answer_prompt}]
    
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

