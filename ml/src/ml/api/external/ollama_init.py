import asyncio
import logging
import os
from collections.abc import Iterator
from typing import Any

import ollama
from ollama import ListResponse

from ml.api.external.ollama_client import EmbeddingModelClient, ReasoningModelClient
from ml.configs import MODEL_ENV_VARS
from ml.domain.models import ChatHistory
from ml.utils import format_progress

logger: logging.Logger = logging.getLogger(__name__)


async def fetch_available_models() -> list[str]:
    """
    getting list of all available model names
    """
    response: ListResponse = await asyncio.to_thread(ollama.list)

    model_names: list[str] = [model.model for model in response.models if model.model is not None]

    if model_names:
        logger.info("Available Ollama models: %s", ", ".join(model_names))
    else:
        logger.info("No Ollama models are currently downloaded.")

    return model_names


async def get_models_from_env() -> list[str]:
    """
    Read .env to get the configured model identifiers
    """

    requested_model_names: list[str] = []
    chat_model_name: str | None = os.getenv(MODEL_ENV_VARS["chat"])
    if chat_model_name is None:
        # If reasoning model is not provided, app can't work
        logger.exception(f"{MODEL_ENV_VARS['chat']} environment varaible is not setted up")
        raise RuntimeError("Cannot run this app without reasoning model setup")
    else:
        requested_model_names.append(chat_model_name)

    embedding_model_name: str | None = os.getenv(MODEL_ENV_VARS["embedding"])
    if embedding_model_name is None:
        # Without embedding model we just skip work of memories
        logger.warning(f"{MODEL_ENV_VARS['embedding']} is not setted up\ncontinuing work without it")
    else:
        requested_model_names.append(embedding_model_name)

    return requested_model_names


async def download_missing_models(available_models: list[str], requested_models: list[str]) -> None:
    """Download all models that are requested but not yet available.

    Logs progress only when a new 5% boundary is reached (5%, 10%, ..., 100%).
    """
    to_download: list[str] = [model for model in requested_models if model not in available_models]

    if not to_download:
        logger.info("All required models are downloaded")
        return

    logger.info("Downloading missing models: %s", ", ".join(to_download))

    def _pull_model(model_name: str) -> None:
        logger.info("Starting download for %s", model_name)

        download_stream: Iterator[ollama.ProgressResponse] = ollama.pull(
            model=model_name,
            stream=True,
        )

        last_step_percent: int | None = None  # last logged multiple of 5; None = nothing logged yet

        for progress in download_stream:
            completed = progress.completed
            total = progress.total

            if completed is not None and total:
                # Compute current percentage and snap it to the latest multiple of 5.
                ratio = max(0.0, min(1.0, completed / total))
                percent_int = int(ratio * 100)
                step_percent = (percent_int // 5) * 5  # 0, 5, 10, ...

                # We only log when we've *finished* a new distinct 5% chunk:
                #   - skip < 5% entirely (no 0% spam),
                #   - log once at 5%, 10%, ..., 100%.
                if step_percent < 5:
                    continue
                if last_step_percent is not None and step_percent <= last_step_percent:
                    continue

                last_step_percent = step_percent
                logger.info("Downloading %s: %s", model_name, format_progress(progress))

            else:
                # total is unknown -> log only once per model to avoid spam
                if last_step_percent is not None:
                    continue
                last_step_percent = 0
                logger.info("Downloading %s: %s", model_name, format_progress(progress))

        logger.info("Finished download for %s", model_name)

    for model in to_download:
        await asyncio.to_thread(_pull_model, model)

    logger.info("All required models are downloaded")


async def init_warmup_clients() -> dict[str, Any]:
    return {"chat": ReasoningModelClient(), "embeddings": EmbeddingModelClient()}


async def _embedding_warmup(client: EmbeddingModelClient) -> None:
    await client.call(content="a")
    return


async def _reasoning_warmup(client: ReasoningModelClient) -> None:
    prompt: ChatHistory = ChatHistory()
    prompt.add_or_change_system(
        content="This is just model warmup call, don't think and reply as fast as possible"
    )
    prompt.add_user(content="Hello, say 'hello' to me as well and nothing else")
    await client.call(messages=prompt)


async def clients_warmup(models: dict[str, Any]) -> None:
    logger.info("Started embedding client warmup")
    await _embedding_warmup(models["embeddings"])
    logger.info("Started reasoner client warmup")
    await _reasoning_warmup(models["chat"])
    return
