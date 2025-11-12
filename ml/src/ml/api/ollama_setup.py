import logging
import os
from typing import Any, Dict, List, Literal

import ollama
from fastapi.encoders import jsonable_encoder

from ml.api.ollama_calls import (
    ModelClient,
    _EmbeddingModelClient,
    _ReasoningModelClient,
    make_client,
)
from ml.configs.model_config import ModelSettings


logger = logging.getLogger(__name__)

_MODEL_ENV_VARS = [
    "OLLAMA_REASONING_MODEL",
    "OLLAMA_EMBEDDING_MODEL",
]

async def get_models_from_env() -> List[str]:
    """Read .env to get the configured model identifiers."""

    requested_model_names: List[str] = []
    for key in _MODEL_ENV_VARS:
        model_name = os.getenv(key)
        requested_model_names.append(model_name)
    return requested_model_names


async def fetch_available_models() -> List[str]:
    """Return Ollama's reported model names and log what is available."""

    response = ollama.list()
    json_models = jsonable_encoder(response)
    entries = json_models.get("models", []) or []

    model_names = [entry["model"] for entry in entries if isinstance(entry, dict)]

    if model_names:
        logger.info("Available Ollama models: %s", ", ".join(model_names))
    else:
        logger.info("No Ollama models are currently downloaded.")

    return model_names


async def download_missing_models(
    available_models: List[str], requested_models: List[str]
) -> None:
    """Download any models that are requested but not yet available."""

    to_download = [model for model in requested_models if model not in available_models]
    if to_download:
        logger.info("Downloading missing models: %s", ", ".join(to_download))
        for model in to_download:
            ollama.pull(model=model)
    logger.info("All required models are downloaded")


async def init_models() -> Dict[str, Any]:
    """Prepare LangGraph clients for every supported mode."""

    model_clients = {
        "chat": _create_reasoning_client(),
        "embeddings": _create_embeddings_client(),
    }
    return model_clients


def _create_reasoning_client() -> Any:
    return make_client(ModelSettings(api_mode="chat", keep_alive=-1))


def _create_embeddings_client() -> Any:
    return make_client(ModelSettings(api_mode="embeddings", keep_alive=-1))


async def warmup_models(clients: Dict[Literal["embeddings", "chat"], ModelClient]) -> None:
    logger.info("Started embedding client warmup")
    await _warmup_embedding(clients["embeddings"])
    logger.info("Started reasoner client warmup")
    await _warmup_reasoner(clients["chat"])


async def _warmup_embedding(client: _EmbeddingModelClient) -> None:
    try:
        await client.call("Test")
        logger.info("Embedding warmup successful")
    except Exception as exc:
        logger.exception("Embedding warmup failed")
        raise RuntimeError("Embedding client warmup failed") from exc


async def _warmup_reasoner(client: _ReasoningModelClient) -> None:
    try:
        await client.call(
            [
                {
                    "role": "system",
                    "content": "This is just model warmup call, don't think and reply as fast as possible",
                },
                {"role": "user", "content": "Hello, say 'hello' to me as well and nothing else"},
            ]
        )
        logger.info("Reasoner warmup successful")
    except Exception as exc:
        logger.exception("Reasoner warmup failed")
        raise RuntimeError("Reasoner client warmup failed") from exc
