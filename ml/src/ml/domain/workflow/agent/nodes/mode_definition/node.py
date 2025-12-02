from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import ChatHistory, GraphState, ModelMode

from .prompt import get_mode_definition_prompt
from .schema import ModeDecisionResponse


async def define_mode(state: GraphState) -> GraphState:
    if state.model_mode == ModelMode.Auto:
        prompt: ChatHistory = await get_mode_definition_prompt(state.chat.last_message())

        client = ReasoningModelClient.instance()

        response = await client.call_structured(messages=prompt, output_schema=ModeDecisionResponse)

        state.model_mode = ModelMode(response.mode.value)

    return state
