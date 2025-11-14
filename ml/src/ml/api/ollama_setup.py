import asyncio
import logging
import os
from typing import Literal

import ollama
from fastapi.encoders import jsonable_encoder
from ml.api.ollama_calls import EmbeddingModelClient, ReasoningModelClient
from ml.configs.message import ChatHistory
from ollama import ListResponse

logger: logging.Logger = logging.getLogger(__name__)

_MODEL_ENV_VARS: list[str] = [
    "OLLAMA_REASONING_MODEL",
    "OLLAMA_EMBEDDING_MODEL",
]


async def get_models_from_env() -> list[str]:
    """Read .env to get the configured model identifiers."""

    requested_model_names: list[str] = []
    for key in _MODEL_ENV_VARS:
        model_name = os.getenv(key)
        requested_model_names.append(model_name)
    return requested_model_names


async def download_missing_models(available_models: list[str], requested_models: list[str]) -> None:
    to_download = [model for model in requested_models if model not in available_models]
    if to_download:
        logger.info("Downloading missing models: %s", ", ".join(to_download))
        for model in to_download:
            ollama.pull(model=model)
    logger.info("All required models are downloaded")


async def init_models() -> dict[str, ReasoningModelClient | EmbeddingModelClient]:
    logger.info("Initializing model clients for warmup")
    return {"chat": ReasoningModelClient(), "embeddings": EmbeddingModelClient()}


async def fetch_available_models() -> list[str]:
    response: ListResponse = ollama.list()
    json_models = jsonable_encoder(response)
    entries = json_models.get("models", []) or []

    model_names = [entry["model"] for entry in entries if isinstance(entry, dict)]

    if model_names:
        logger.info("Available Ollama models: %s", ", ".join(model_names))
    else:
        logger.info("No Ollama models are currently downloaded.")

    return model_names


async def fetch_running_models() -> list[str]:
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
    clients: dict[Literal["embeddings", "chat"], ReasoningModelClient | EmbeddingModelClient],
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
    prompt: ChatHistory = ChatHistory()
    prompt.add_or_change_system(
        content="This is just model warmup call, don't think and reply as fast as possible"
    )
    prompt.add_user(content="Hello, say 'hello' to me as well and nothing else")
    try:
        await asyncio.to_thread(client.call, prompt)
        logger.info("Reasoner warmup successful")
    except Exception as exc:
        logger.exception("Reasoner warmup failed")
        raise RuntimeError("Reasoner client warmup failed") from exc
