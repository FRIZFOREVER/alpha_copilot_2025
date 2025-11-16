import asyncio
import logging
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from ollama import ChatResponse

from ml.agent.router import workflow, workflow_collected
from ml.api.ollama_setup import (
    download_missing_models,
    fetch_available_models,
    fetch_running_models,
    get_models_from_env,
    init_models,
    warmup_models,
)
from ml.api.types import ModelClients
from ml.configs.message import RequestPayload, Tag

logger: logging.Logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.models_ready = asyncio.Event()

    async def _init() -> None:
        # checking and download missing models
        available_models: list[str] = await fetch_available_models()
        requested_models: list[str] = await get_models_from_env()
        await download_missing_models(available_models, requested_models)

        # Init and warmup
        models: ModelClients = await init_models()
        await warmup_models(models)
        app.state.models_ready.set()
        logger.info("All models successfully initialized, ready to accept connections")

    app.state.models_task = asyncio.create_task(_init())

    yield


def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API", lifespan=lifespan)

    @app.post("/message")
    async def message(payload: RequestPayload) -> JSONResponse:  # type: ignore[reportUnusedFunction]
        # Check if models are initialized
        if not app.state.models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        message_text: str
        tag: Tag
        try:
            message_text, tag = workflow_collected(payload)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response from collect workflow",
            ) from exc

        return JSONResponse(
            content={"message": message_text}, headers={"Tag": tag.value}
        )

    @app.post("/message_stream")
    async def message_stream(payload: RequestPayload) -> StreamingResponse:  # type: ignore[reportUnusedFunction]
        # Check if models are initialized
        if not app.state.models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        stream: Iterator[ChatResponse]
        tag: Tag
        stream, tag = workflow(payload)

        def event_generator(stream: Iterator[ChatResponse]) -> Iterator[str]:
            for chunk in stream:
                yield f"data: {chunk.model_dump_json()}\n\n"

        headers: dict[str, Any] = {"tag": tag.value}
        return StreamingResponse(
            event_generator(stream=stream),
            media_type="text/event-stream",
            headers=headers,
        )

        # функция принимает стринг, отдает

    @app.get("/ping")
    def ping() -> dict[str, str]:  # type: ignore[reportUnusedFunction]
        return {"message": "pong"}

    @app.get("/ollama")
    async def ollama_models() -> dict[str, list[str]]:  # type: ignore[reportUnusedFunction]
        available_models = await fetch_available_models()
        running_models = await fetch_running_models()
        return {
            "available_models": available_models or [],
            "running_models": running_models or [],
        }

    @app.get("/health")
    def healthcheck() -> dict[str, str]:  # type: ignore[reportUnusedFunction]
        return {"status": "healthy"}

    return app
