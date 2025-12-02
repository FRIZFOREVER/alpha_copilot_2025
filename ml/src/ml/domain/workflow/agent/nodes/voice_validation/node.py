from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import GraphState

from .prompt import get_voice_validation_prompt
from .schema import VoiceValidationResponse


async def validate_voice(state: GraphState) -> GraphState:
    if state.meta.is_voice:
        prompt = get_voice_validation_prompt(state.chat.last_message())
        client = ReasoningModelClient.instance()

        response: VoiceValidationResponse = await client.call_structured(
            messages=prompt, output_schema=VoiceValidationResponse
        )

        state.voice_is_valid = response.voice_is_valid

        # TODO: Add logic for returning mock message as a stream
    return state
