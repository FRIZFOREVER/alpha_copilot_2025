import logging

from ml.api.external import send_graph_log
from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import GraphState, PicsTags

from .prompt import get_voice_validation_prompt
from .schema import VoiceValidationResponse


logger = logging.getLogger(__name__)


async def validate_voice(state: GraphState) -> GraphState:
    logger.info("Entering validate_voice node")

    if state.meta.is_voice:
        answer_id = state.chat.last_user_message_id()

        await send_graph_log(
            chat_id=state.chat_id,
            tag=PicsTags.Mic,
            message="Распознаю голосовой запрос",
            answer_id=answer_id,
        )

        prompt = get_voice_validation_prompt(state.chat.last_message())
        client = ReasoningModelClient.instance()

        response: VoiceValidationResponse = await client.call_structured(
            messages=prompt, output_schema=VoiceValidationResponse
        )

        state.voice_is_valid = response.voice_is_valid

        # TODO: Add logic for returning mock message as a stream
    return state
