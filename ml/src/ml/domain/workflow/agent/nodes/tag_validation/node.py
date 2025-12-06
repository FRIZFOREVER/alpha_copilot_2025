import logging

from ml.api.external import send_graph_log
from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import ChatHistory, GraphState, PicsTags, Tag

from .prompt import get_tag_validation_prompt
from .schema import DefinedTag

logger = logging.getLogger(__name__)


async def validate_tag(state: GraphState) -> GraphState:
    logger.info("Entering validate_tag node")

    if state.meta.tag == Tag.Empty:
        logger.info("Tag is considered as Empty, defining Tag")

        answer_id = state.chat.last_user_message_id()

        await send_graph_log(
            chat_id=state.chat_id, tag=PicsTags.Think, message="Определяю Tag", answer_id=answer_id
        )

        prompt: ChatHistory = get_tag_validation_prompt(state.chat.last_message())

        client = ReasoningModelClient.instance()

        result = await client.call_structured(messages=prompt, output_schema=DefinedTag)

        state.meta.tag = result.tag

    logger.info("Tag: %s", state.meta.tag)
    return state
