import logging

from ml.api.external.ollama_client import EmbeddingModelClient, ReasoningModelClient
from ml.api.schemas.client_types import ModelClients
from ml.domain.models import ChatHistory

logger = logging.getLogger(__name__)


async def init_warmup_clients() -> ModelClients:
    chat_client = ReasoningModelClient()
    embedding_client = EmbeddingModelClient()

    return {"chat": chat_client, "embeddings": embedding_client}


async def _embedding_warmup(client: EmbeddingModelClient) -> None:
    await client.call(content="a")
    return


async def _reasoning_warmup(client: ReasoningModelClient) -> None:
    prompt: ChatHistory = ChatHistory()
    prompt.add_or_change_system(
        content="This is just model warmup call, don't think and reply as fast as possible"
    )
    prompt.add_user(content="Hello, say 'hello' to me as well and nothing else")
    await client.call(messages=prompt)


async def clients_warmup(models: ModelClients) -> None:
    logger.info("Started embedding client warmup")
    await _embedding_warmup(models["embeddings"])

    logger.info("Started reasoner client warmup")
    await _reasoning_warmup(models["chat"])
    return
