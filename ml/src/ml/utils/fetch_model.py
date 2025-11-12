import asyncio
from collections.abc import Iterable
from typing import Dict, Optional, Set

import ollama

from ml.configs.model_config import list_configured_models


def get_configured_model_ids() -> Set[str]:
    """Return the set of configured Ollama model identifiers."""

    configured_models = {
        model.strip()
        for model in list_configured_models().values()
        if isinstance(model, str) and model.strip()
    }
    return configured_models


async def _pull_model(model: str) -> bool:
    try:
        await asyncio.to_thread(ollama.pull, model)
    except Exception:
        return False

    return True


async def fetch_models() -> Dict[str, bool]:
    """Fetch configured models and return per-model success flags."""

    models = sorted(get_configured_model_ids())
    if not models:
        return {}

    results = await asyncio.gather(*(_pull_model(model) for model in models))
    return dict(zip(models, results))


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
    try:
        await asyncio.to_thread(ollama.delete, model)
    except Exception:
        return False

    return True


async def prune_unconfigured_models() -> Dict[str, bool]:
    """Remove Ollama models that are not configured and return deletion results."""

    configured_models = get_configured_model_ids()
    listed_models = await asyncio.to_thread(ollama.list)
    available_models = _extract_model_names(listed_models)
    extras = sorted(available_models - configured_models)

    if not extras:
        return {}

    results = await asyncio.gather(*(_delete_model(model) for model in extras))
    return dict(zip(extras, results))


async def delete_models() -> Dict[str, bool]:
    """Alias for :func:`prune_unconfigured_models` to match legacy callers."""

    return await prune_unconfigured_models()
