import logging

from ml.api.external.ollama_client import ReasoningModelClient
from ml.domain.models import ChatHistory, GraphState

logger = logging.getLogger(__name__)


async def final_stream(state: GraphState) -> GraphState:
    client = ReasoningModelClient.instance()

    if state.final_prompt:
        prompt: ChatHistory = state.final_prompt
    else:
        msg = "Inside final stream node: final prompt is None, cannot generate final stream"
        logger.error(msg)
        raise RuntimeError(msg)

    result = client.stream(messages=prompt)

    state.output_stream = result

    return state
