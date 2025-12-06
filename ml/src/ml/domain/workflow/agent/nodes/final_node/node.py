import logging
from collections.abc import AsyncIterator

from ml.api.external import send_graph_log
from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import ChatHistory, GraphState, PicsTags

logger = logging.getLogger(__name__)


async def final_stream(state: GraphState) -> GraphState:
    logger.info("Entering final_stream node")

    client = ReasoningModelClient.instance()

    answer_id = state.chat.last_user_message_id()

    await send_graph_log(
        chat_id=state.chat_id, tag=PicsTags.Think, message="Генерирую ответ", answer_id=answer_id
    )

    prompt = state.final_prompt
    if prompt is None:
        msg = "Inside final stream node: final prompt is None, cannot generate final stream"
        logger.error(msg)
        raise RuntimeError(msg)
    if not isinstance(prompt, ChatHistory):
        raise TypeError("Final prompt must be an instance of ChatHistory")

    logger.info("final_prompt: %s", prompt.model_dump_json(indent=2))
    result = client.stream(messages=prompt)
    if not isinstance(result, AsyncIterator):
        msg = "Reasoning client stream did not return an AsyncIterator"
        logger.error(msg)
        raise TypeError(msg)

    state.output_stream = result

    return state
