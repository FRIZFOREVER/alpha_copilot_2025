import asyncio
from typing import Dict, List

from ml.agent.calls.model_calls import (
    ModelClient,
    _EmbeddingModelClient,
    _ReasoningModelClient,
    _RerankModelClient,
)


async def warmup_models(clients: List[ModelClient]) -> Dict[str, bool]:
    """Warm up provided model clients and return per-model outcomes."""

    embedding_and_rerank_clients: List[ModelClient] = []
    reasoning_clients: List[ModelClient] = []

    for client in clients:
        if isinstance(client, _ReasoningModelClient):
            reasoning_clients.append(client)
        else:
            embedding_and_rerank_clients.append(client)

    results: Dict[str, bool] = {}

    if embedding_and_rerank_clients:
        statuses = await asyncio.gather(
            *(_warmup_client(client) for client in embedding_and_rerank_clients)
        )
        for client, status in zip(embedding_and_rerank_clients, statuses):
            results[client.s.model] = status

    for client in reasoning_clients:
        results[client.s.model] = await _warmup_client(client)

    return results


async def _warmup_client(client: ModelClient) -> bool:
    try:
        await _invoke_warmup_call(client)
    except Exception:
        return False
    return True


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
