import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from ml.api.external import (
    clients_warmup,
    download_missing_models,
    fetch_available_models,
    get_models_from_env,
    init_graph_log_client,
    init_warmup_clients,
)
from ml.api.routes.health import router as health_router
from ml.api.routes.workflow import router as workflow_router
from ml.configs import LLMMode, get_llm_mode

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model_ready = asyncio.Event()

    async def _init() -> None:
        mode = get_llm_mode()
        logger.info("Starting model initialization for mode=%s", mode.value)

        try:
            if mode is LLMMode.OLLAMA:
                available_models = await fetch_available_models()
                requested_models = await get_models_from_env()

                await download_missing_models(available_models, requested_models)
            else:
                logger.info(
                    "Skipping local model discovery and download for non-Ollama mode=%s", mode.value
                )

            await init_warmup_clients()
            await clients_warmup()

            app.state.graph_log_client = await init_graph_log_client()

            logger.info(
                "Model initialization completed for mode=%s; ready to accept connections",
                mode.value,
            )
        except Exception:
            logger.exception("Failed to initialize models for mode %s", mode.value)
            raise
        finally:
            app.state.model_ready.set()

    app.state.models_task = asyncio.create_task(_init())

    def _log_models_task(task: asyncio.Task[Any]) -> None:
        try:
            task.result()
        except Exception:
            logger.exception("Model initialization task failed")

    app.state.models_task.add_done_callback(_log_models_task)

    yield

    await app.state.models_task


def app() -> FastAPI:
    app = FastAPI(title="ml service", lifespan=lifespan)

    # /ping
    app.include_router(health_router)

    # /message_stream and /message
    app.include_router(workflow_router)

    return app
