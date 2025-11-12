import asyncio
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
import ollama

from ml.agent.router import init_models, workflow_collect, workflow_stream
from ml.configs.message import RequestPayload
from ml.utils.fetch_model import delete_models, fetch_models, prune_unconfigured_models
from ml.utils.warmup import warmup_models


async def lifespan(app: FastAPI):
    app.state.models = None
    app.state.models_ready = asyncio.Event()
    app.state.model_fetch_result = {}
    app.state.model_prune_result = {}
    app.state.model_warmup_result = {}
    app.state.model_cleanup_result = {}

    async def _init():
        app.state.model_fetch_result = await fetch_models()
        app.state.model_prune_result = await prune_unconfigured_models()
        models = await init_models()
        app.state.model_warmup_result = await warmup_models(list(models.values()))
        app.state.models = models
        app.state.models_ready.set()

    app.state.models_task = asyncio.create_task(_init())

    yield

    app.state.model_cleanup_result = await delete_models()



def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API", lifespan=lifespan)

    @app.post("/message")
    async def message(payload: RequestPayload) -> Dict[str, str]:
        models_ready = app.state.models_ready

        if not models_ready.is_set():
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
        models_ready = app.state.models_ready

        if not models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        def event_generator():
            stream = workflow_stream(payload.model_dump())
            for chunk in stream:
                yield f"data: {chunk.model_dump_json()}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.post("/mock")
    def mock():
        return {"message": "No, you"}

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
