import asyncio
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
import ollama

from ml.agent.router import workflow_collect, workflow_stream
from ml.configs.message import RequestPayload
import ml.api.ollama_setup as ollama_setup

import logging

logger = logging.getLogger(__name__)

async def lifespan(app: FastAPI):
    app.state.models_ready = asyncio.Event()

    async def _init():
        # checking and download missing models
        available_models: List[str] = await ollama_setup.fetch_available_models()
        requested_models: List[str] = await ollama_setup.get_models_from_env()
        await ollama_setup.download_missing_models(available_models, requested_models)

        # Init and warmup
        models = await ollama_setup.init_models()
        await ollama_setup.warmup_models(models)
        app.state.models_ready.set()

    app.state.models_task = asyncio.create_task(_init())

    yield


def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API", lifespan=lifespan)

    @app.post("/message")
    async def message(payload: RequestPayload) -> Dict[str, str]:

        # Check if models are initialized by now
        if not app.state.models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        try:
            message_text = workflow_collect(payload.model_dump())
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail="Failed to generate response from workflow"
            ) from exc

        return {"message": message_text}

    @app.post("/message_stream")
    async def message_stream(payload: RequestPayload) -> StreamingResponse:

        # Check if models are initialized by now
        if not app.state.models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        def event_generator():
            stream = workflow_stream(payload.model_dump())
            for chunk in stream:
                yield f"data: {chunk.model_dump_json()}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"message": "pong"}

    @app.get("/ollama")
    async def ollama_models() -> Dict[str, Any]:
        try:
            models = await asyncio.to_thread(ollama.list)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Failed to fetch ollama models",
            ) from exc

        return jsonable_encoder(models)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "healthy"}

    return app
