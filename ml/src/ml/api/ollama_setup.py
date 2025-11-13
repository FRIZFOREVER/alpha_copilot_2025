import asyncio
import logging
import os
from typing import Any, Dict, List, Literal, Union

from ml.api.ollama_calls import EmbeddingModelClient, ReasoningModelClient
import ollama
from fastapi.encoders import jsonable_encoder


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


async def download_missing_models(
    available_models: List[str], requested_models: List[str]
) -> None:
    to_download = [model for model in requested_models if model not in available_models]
    if to_download:
        logger.info("Downloading missing models: %s", ", ".join(to_download))
        for model in to_download:
            ollama.pull(model=model)
    logger.info("All required models are downloaded")


async def init_models() -> Dict[str, Union[ReasoningModelClient, EmbeddingModelClient]]:
    logger.info("Initializing model clients for warmup")
    return {
        "chat": ReasoningModelClient(),
        "embeddings": EmbeddingModelClient()
    }

async def fetch_available_models() -> List[str]:
    response = ollama.list()
    json_models = jsonable_encoder(response)
    entries = json_models.get("models", []) or []

    model_names = [entry["model"] for entry in entries if isinstance(entry, dict)]

    if model_names:
        logger.info("Available Ollama models: %s", ", ".join(model_names))
    else:
        logger.info("No Ollama models are currently downloaded.")

    return model_names

async def fetch_running_models() -> List[str]:
    response = ollama.ps()
    json_models = jsonable_encoder(response)
    entries = (
        json_models.get("models", [])
        or json_models.get("running", [])
        or json_models.get("processes", [])
    )

    running = [
        entry["model"]
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("model"), str)
    ]

    if running:
        logger.info("Running Ollama models: %s", ", ".join(running))
    else:
        logger.info("No Ollama models are currently running.")

    return running


async def warmup_models(
        clients: Dict[Literal["embeddings", "chat"], 
                      Union[ReasoningModelClient, EmbeddingModelClient]]
                      ) -> None:
    logger.info("Started embedding client warmup")
    await _warmup_embedding(clients["embeddings"])
    logger.info("Started reasoner client warmup")
    await _warmup_reasoner(clients["chat"])


async def _warmup_embedding(client: EmbeddingModelClient) -> None:
    try:
        await asyncio.to_thread(client.call, "Test")
        logger.info("Embedding warmup successful")
    except Exception as exc:
        logger.exception("Embedding warmup failed")
        raise RuntimeError("Embedding client warmup failed") from exc


async def _warmup_reasoner(client: ReasoningModelClient) -> None:
    messages: List[Dict[str, str]] = [
                {
                    "role": "system",
                    "content": "This is just model warmup call, don't think and reply as fast as possible",
                },
                {"role": "user", "content": "Hello, say 'hello' to me as well and nothing else"},
            ]
    try:
        await asyncio.to_thread(client.call, messages)
        logger.info("Reasoner warmup successful")
    except Exception as exc:
        logger.exception("Reasoner warmup failed")
        raise RuntimeError("Reasoner client warmup failed") from exc
