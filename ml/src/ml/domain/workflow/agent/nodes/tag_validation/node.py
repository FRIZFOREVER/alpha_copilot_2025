import logging

from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import ChatHistory, GraphState, Tag

from .prompt import get_tag_validation_prompt
from .schema import DefinedTag


logger = logging.getLogger(__name__)


async def validate_tag(state: GraphState) -> GraphState:
    logger.info("Entering validate_tag node")

    if state.meta.tag == Tag.Empty:
        prompt: ChatHistory = get_tag_validation_prompt(state.chat.last_message())

        client = ReasoningModelClient.instance()

        result = await client.call_structured(messages=prompt, output_schema=DefinedTag)

        state.meta.tag = result.tag

    return state
