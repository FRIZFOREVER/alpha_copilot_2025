import logging

from ml.api.external.ollama_client import EmbeddingModelClient, ReasoningModelClient
from ml.configs import LLMMode, get_llm_mode
from ml.domain.models import ChatHistory

logger = logging.getLogger(__name__)


async def init_warmup_clients():
    mode = get_llm_mode()

    logger.debug("Initiating ReasoningModelClient for mode=%s", mode.value)
    ReasoningModelClient.instance()

    logger.debug("Initiating EmbeddingModelClient for mode=%s", mode.value)
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
    mode = get_llm_mode()

    if mode is not LLMMode.OLLAMA:
        logger.info("Skipping local client warmup for remote mode=%s", mode.value)
        return

    logger.info("Started embedding client warmup for mode=%s", mode.value)
    await _embedding_warmup()

    logger.info("Started reasoner client warmup for mode=%s", mode.value)
    await _reasoning_warmup()


async def close_clients() -> None:
    logger.debug("Closing reasoner warmup client")
    ReasoningModelClient.reset_instance()

    logger.debug("Closing embedding warmup client")
    EmbeddingModelClient.reset_instance()
