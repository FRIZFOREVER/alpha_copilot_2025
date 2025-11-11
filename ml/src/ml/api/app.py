import asyncio
import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
import ollama

from ml.agent.router import init_models, workflow_collect, workflow_stream

logger = logging.getLogger(__name__)

async def lifespan(app: FastAPI):
    app.state.models = None
    app.state.models_ready = asyncio.Event()
    
    async def _init():
        models = await init_models()
        app.state.models = models
        app.state.models_ready.set()

    app.state.models_task = asyncio.create_task(_init())

    yield


def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API", lifespan=lifespan)
    logger.info("FastAPI application initialised")

    @app.post("/message")
    async def message(request: Request) -> Dict[str, str]:
        models_ready = app.state.models_ready

        if not models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        payload: Dict[str, Any] = await request.json()
        logger.info("Handling /message request with payload")

        try:
            message_text = workflow_collect(payload)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Failed to generate response from workflow")
            raise HTTPException(
                status_code=500, detail="Failed to generate response from workflow"
            ) from exc

        return {"message": message_text}
    
    @app.post("/message_stream")
    async def message_stream(request: Request) -> StreamingResponse:
        models_ready = app.state.models_ready

        if not models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        payload: Dict[str, Any] = await request.json()
        logger.info("Handling /message_stream request with payload")

        def event_generator():
            stream = workflow_stream(payload)
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
