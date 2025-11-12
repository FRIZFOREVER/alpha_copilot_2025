import asyncio
import logging

import ollama 

from ml.configs.model_config import _MODEL_NAMES_DICT

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def fetch_models() -> None:
    for model in _MODEL_NAMES_DICT.values():
        logger.debug(f"Start fetch {model}")
        if not model:
            continue
        try:
            await asyncio.to_thread(ollama.pull, model)
        except Exception:
            logger.warning("Model %s pull failed", model, exc_info=True)


async def delete_models() -> None:
    for model in _MODEL_NAMES_DICT.values():
        logger.debug(f"Start delete {model}")
        if not model:
            continue
        try:
            await asyncio.to_thread(ollama.delete, model)
        except Exception:
            logger.warning("Model %s pull failed", model, exc_info=True)