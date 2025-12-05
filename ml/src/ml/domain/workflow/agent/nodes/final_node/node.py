import logging

from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import ChatHistory, GraphState

logger = logging.getLogger(__name__)


async def final_stream(state: GraphState) -> GraphState:
    client = ReasoningModelClient.instance()

    prompt = state.final_prompt
    if prompt is None:
        msg = "Inside final stream node: final prompt is None, cannot generate final stream"
        logger.error(msg)
        raise RuntimeError(msg)
    if not isinstance(prompt, ChatHistory):
        raise TypeError("Final prompt must be an instance of ChatHistory")

    result = await client.stream(messages=prompt)

    state.output_stream = result

    return state
