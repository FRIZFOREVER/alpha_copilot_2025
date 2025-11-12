import asyncio
import logging

import ollama

from ml.configs.model_config import list_configured_models

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def fetch_models() -> None:
    for model in list_configured_models().values():
        logger.debug("Start fetch %s", model)
        if not model:
            continue
        try:
            await asyncio.to_thread(ollama.pull, model)
        except Exception:
            logger.warning("Model %s pull failed", model, exc_info=True)


async def delete_models() -> None:
    for model in list_configured_models().values():
        logger.debug("Start delete %s", model)
        if not model:
            continue
        try:
            await asyncio.to_thread(ollama.delete, model)
        except Exception:
            logger.warning("Model %s delete failed", model, exc_info=True)
