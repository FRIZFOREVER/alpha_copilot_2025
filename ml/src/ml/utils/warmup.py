import asyncio
import logging
from typing import List

from ml.agent.calls.model_calls import (
    ModelClient,
    _EmbeddingModelClient,
    _ReasoningModelClient,
    _RerankModelClient,
)
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def warmup_models(clients: List[ModelClient]) -> None:
    logger.debug("Start warmup")

    embedding_and_rerank_clients: List[ModelClient] = []
    reasoning_clients: List[ModelClient] = []

    for client in clients:
        if isinstance(client, _ReasoningModelClient):
            reasoning_clients.append(client)
        else:
            embedding_and_rerank_clients.append(client)

    if embedding_and_rerank_clients:
        await asyncio.gather(
            *(_warmup_client(client) for client in embedding_and_rerank_clients)
        )

    for client in reasoning_clients:
        await _warmup_client(client)


async def _warmup_client(client: ModelClient) -> None:
    logger.debug("Start warmup %s", client.s.model)

    try:
        await _invoke_warmup_call(client)
    except Exception as exc:  # pragma: no cover - logging path
        logger.warning("Model %s warm-up failed", client.s.model, exc_info=exc)
    else:
        logger.info("Model %s warmed up", client.s.model)


async def _invoke_warmup_call(client: ModelClient) -> None:
    if isinstance(client, _EmbeddingModelClient):
        await asyncio.to_thread(client.call, "warm-up text")
        return

    if isinstance(client, _RerankModelClient):
        messages = [
            {"role": "system", "content": "You rerank answers by returning yes/no."},
            {"role": "user", "content": "Is this relevant?"},
        ]
    else:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "ping"},
        ]

    await asyncio.to_thread(client.call, messages)
