import asyncio
import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
import ollama

from ml.agent.router import workflow, init_models
from ml.configs.message import RequestPayload
from ml.utils.fetch_model import fetch_models
from ml.utils.warmup import warmup_models


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def lifespan(app: FastAPI):
    app.state.models = None
    app.state.models_ready = asyncio.Event()
    
    async def _init():
        try:
            await fetch_models()
        except Exception:
            logger.warning("Failed to prefetch models via Ollama", exc_info=True)
        models = await init_models()
        try:
            await warmup_models(list(models.values()))
        except Exception:
            logger.warning("Failed to warmup models", exc_info=True)
        app.state.models = models
        app.state.models_ready.set()

    app.state.models_task = asyncio.create_task(_init())

    yield


def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API", lifespan=lifespan)
    logger.info("FastAPI application initialised")

    @app.post("/message")
    async def message(payload: RequestPayload) -> Dict[str, str]:
        models_ready = app.state.models_ready

        if not models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        logger.info("Handling /message request with payload")
        answer = workflow(payload.model_dump())
        return {"message": answer}
    
    @app.post("/message_stream")
    async def message_stream(payload: RequestPayload) -> StreamingResponse:
        models_ready = app.state.models_ready

        if not models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        logger.info("Handling /message_stream request with payload")

        def event_generator():
            stream = workflow(payload.model_dump(), streaming=True)
            for chunk in stream:
                yield f"data: {chunk.model_dump_json()}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    @app.post("/mock")
    def mock():
        return {"message": "No, you"}

    @app.get("/ping")
    def ping() -> dict[str, str]:
        logger.debug("Handling /ping request")
        return {"message": "pong"}

    @app.get("/ollama")
    async def ollama_models() -> Dict[str, Any]:
        logger.debug("Handling /ollama request")
        try:
            models = await asyncio.to_thread(ollama.list)
        except Exception as exc:
            logger.exception("Failed to fetch ollama models")
            raise HTTPException(
                status_code=503,
                detail="Failed to fetch ollama models",
            ) from exc

        return jsonable_encoder(models)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        logger.debug("Handling /health request")
        return {"status": "healthy"}

    return app
