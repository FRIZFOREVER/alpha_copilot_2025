import asyncio
import logging
import os
from typing import Any, cast

import ollama
from fastapi.encoders import jsonable_encoder
from ollama import ListResponse, ProcessResponse

from ml.api.ollama_calls import EmbeddingModelClient, ReasoningModelClient
from ml.api.types import ModelClients
from ml.configs.message import ChatHistory

logger: logging.Logger = logging.getLogger(__name__)

_MODEL_ENV_VARS: list[str] = [
    "OLLAMA_REASONING_MODEL",
    "OLLAMA_EMBEDDING_MODEL",
]


async def get_models_from_env() -> list[str]:
    """Read .env to get the configured model identifiers."""

    requested_model_names: list[str] = []
    for key in _MODEL_ENV_VARS:
        model_name: str | None = os.getenv(key)
        if model_name is None:
            logger.exception(f"{key} environment varaible is not setted up")
            raise RuntimeError("Cannot run this app without proper .env setup")
        requested_model_names.append(model_name)
    return requested_model_names


async def download_missing_models(available_models: list[str], requested_models: list[str]) -> None:
    to_download: list[str] = [model for model in requested_models if model not in available_models]
    if to_download:
        logger.info("Downloading missing models: %s", ", ".join(to_download))
        for model in to_download:
            ollama.pull(model=model)
    logger.info("All required models are downloaded")


async def init_models() -> ModelClients:
    logger.info("Initializing model clients for warmup")
    return {"chat": ReasoningModelClient(), "embeddings": EmbeddingModelClient()}


async def fetch_available_models() -> list[str]:
    response: ListResponse = ollama.list()

    model_names: list[str] = [model.model for model in response.models if model.model is not None]

    if model_names:
        logger.info("Available Ollama models: %s", ", ".join(model_names))
    else:
        logger.info("No Ollama models are currently downloaded.")

    return model_names


async def fetch_running_models() -> list[str]:
    response: ProcessResponse = ollama.ps()
    encoded = jsonable_encoder(response)

    entries: list[dict[str, Any]] = []
    if isinstance(encoded, dict):
        json_models = cast(dict[str, Any], encoded)
        candidate_lists: tuple[list[Any] | None, ...] = (
            cast(list[Any] | None, json_models.get("models")),
            cast(list[Any] | None, json_models.get("running")),
            cast(list[Any] | None, json_models.get("processes")),
        )
        for candidate in candidate_lists:
            if isinstance(candidate, list):
                entries = [item for item in candidate if isinstance(item, dict)]
                break

    running: list[str] = [
        model for entry in entries if (model := entry.get("model")) and isinstance(model, str)
    ]

    if running:
        logger.info("Running Ollama models: %s", ", ".join(running))
    else:
        logger.info("No Ollama models are currently running.")

    return running


async def warmup_models(clients: ModelClients) -> None:
    logger.info("Started embedding client warmup")
    await _warmup_embedding(clients["embeddings"])  # pyright: ignore[reportArgumentType]
    logger.info("Started reasoner client warmup")
    await _warmup_reasoner(clients["chat"])  # pyright: ignore[reportArgumentType]
    return


async def _warmup_embedding(client: EmbeddingModelClient) -> None:
    try:
        await asyncio.to_thread(client.call, "Test")  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        logger.info("Embedding warmup successful")
    except Exception as exc:
        logger.exception("Embedding warmup failed")
        raise RuntimeError("Embedding client warmup failed") from exc
    return


async def _warmup_reasoner(client: ReasoningModelClient) -> None:
    prompt: ChatHistory = ChatHistory()
    prompt.add_or_change_system(
        content="This is just model warmup call, don't think and reply as fast as possible"
    )
    prompt.add_user(content="Hello, say 'hello' to me as well and nothing else")
    try:
        await asyncio.to_thread(client.call, prompt)  # type: ignore[reportUnknownArgumentType,reportUnknownMemberType]
        logger.info("Reasoner warmup successful")
    except Exception as exc:
        logger.exception("Reasoner warmup failed")
        raise RuntimeError("Reasoner client warmup failed") from exc
    return
