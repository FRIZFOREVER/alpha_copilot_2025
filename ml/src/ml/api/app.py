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
    init_warmup_clients,
)
from ml.api.routes.health import router as health_router
from ml.api.routes.workflow import router as workflow_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model_ready = asyncio.Event()

    async def _init() -> None:
        logger.info("Starting Ollama model initialization")

        try:
            available_models = await fetch_available_models()
            requested_models = await get_models_from_env()

            await download_missing_models(available_models, requested_models)

            await init_warmup_clients()
            await clients_warmup()

            logger.info("All models successfully initialized, ready to accept connections")
        except Exception:
            logger.exception("Failed to initialize Ollama models")
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
