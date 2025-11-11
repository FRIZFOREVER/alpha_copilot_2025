import asyncio
import logging
from typing import List
from ml.agent.calls.model_calls import ModelClient, _EmbeddingModelClient
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def warmup_models(clients: List[ModelClient]) -> None:
    logger.debug(f"Start warmup")
    
    warmup_tasks = []    
    for client in clients:
        logger.debug(f"Start warmup {client.s.model}")
        if isinstance(client, _EmbeddingModelClient):
            warmup_tasks.append(
                asyncio.to_thread(client.call, "warm-up text")
            )
        else:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "ping"},
            ]
            warmup_tasks.append(
                asyncio.to_thread(client.call, messages)
            )
    
    if warmup_tasks:
        results = await asyncio.gather(*warmup_tasks, return_exceptions=True)
        for client, result in zip(clients, results):
            if isinstance(result, Exception):
                logger.warning("Model %s warm-up failed", client.s.model, exc_info=result)
            else:
                logger.info("Model %s warmed up", client.s.model)