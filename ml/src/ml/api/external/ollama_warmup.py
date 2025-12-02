import logging

from ml.api.external.ollama_client import EmbeddingModelClient, ReasoningModelClient
from ml.domain.models import ChatHistory

logger = logging.getLogger(__name__)


async def init_warmup_clients():
    logger.debug("Initiating ReasoningModelClient")
    ReasoningModelClient.instance()
    logger.debug("Initiating EmbeddingModelClient")
    EmbeddingModelClient.instance()


async def _embedding_warmup() -> None:
    client = EmbeddingModelClient.instance()
    await client.call(content="a")


async def _reasoning_warmup() -> None:
    client = ReasoningModelClient.instance()
    prompt: ChatHistory = ChatHistory()
    prompt.add_or_change_system(
        content="This is just model warmup call, don't think and reply as fast as possible"
    )
    prompt.add_user(content="Hello, say 'hello' to me as well and nothing else")
    # calling with additional max output tokens = 1 for speed
    await client.call(messages=prompt, num_predict=1)


async def clients_warmup() -> None:
    logger.info("Started embedding client warmup")
    await _embedding_warmup()

    logger.info("Started reasoner client warmup")
    await _reasoning_warmup()


async def close_clients() -> None:
    logger.debug("Closing reasoner warmup client")
    ReasoningModelClient.reset_instance()

    logger.debug("Closing embedding warmup client")
    EmbeddingModelClient.reset_instance()
