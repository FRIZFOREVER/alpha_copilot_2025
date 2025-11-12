import asyncio
import logging
from collections.abc import Iterable
from typing import Optional, Set

import ollama

from ml.configs.model_config import list_configured_models

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_configured_model_ids() -> Set[str]:
    """Return the set of configured Ollama model identifiers."""

    configured_models = {
        model.strip()
        for model in list_configured_models().values()
        if isinstance(model, str) and model.strip()
    }
    return configured_models


async def _pull_model(model: str) -> bool:
    logger.debug("Start fetch %s", model)
    try:
        await asyncio.to_thread(ollama.pull, model)
    except Exception:
        logger.warning("Model %s pull failed", model, exc_info=True)
        return False

    logger.info("Model %s pull succeeded", model)
    return True


async def fetch_models() -> None:
    models = sorted(get_configured_model_ids())
    if not models:
        logger.info("No configured models to fetch")
        return

    await asyncio.gather(*(_pull_model(model) for model in models), return_exceptions=True)


def _extract_model_names(raw_models: object) -> Set[str]:
    if isinstance(raw_models, dict):
        iterable: Optional[Iterable[object]] = raw_models.get("models")  # type: ignore[arg-type]
    elif isinstance(raw_models, Iterable) and not isinstance(raw_models, (str, bytes)):
        iterable = raw_models
    else:
        iterable = None

    if not iterable:
        return set()

    names: Set[str] = set()
    for item in iterable:
        if isinstance(item, dict):
            name = item.get("name") or item.get("model")
        elif isinstance(item, str):
            name = item
        else:
            name = None

        if isinstance(name, str) and name.strip():
            names.add(name.strip())

    return names


async def _delete_model(model: str) -> bool:
    logger.debug("Start delete %s", model)
    try:
        await asyncio.to_thread(ollama.delete, model)
    except Exception:
        logger.warning("Model %s delete failed", model, exc_info=True)
        return False

    logger.info("Model %s delete succeeded", model)
    return True


async def prune_unconfigured_models() -> None:
    configured_models = get_configured_model_ids()

    try:
        listed_models = await asyncio.to_thread(ollama.list)
    except Exception:
        logger.warning("Failed to list models for pruning", exc_info=True)
        return

    available_models = _extract_model_names(listed_models)
    extras = sorted(available_models - configured_models)

    if not extras:
        logger.info("No extra models detected during prune")
        return

    await asyncio.gather(*(_delete_model(model) for model in extras), return_exceptions=True)


async def delete_models() -> None:
    await prune_unconfigured_models()
