"""Основной файл приложения FastAPI"""

import asyncio
import logging
from typing import Any

from config import OLLAMA_HOST
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from handlers import (
    ollama as ollama_handlers,
)
from utils.ollama_utils import check_ollama_available, mock_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock ML Service")

app.state.models_ready = asyncio.Event()


@app.on_event("startup")
async def startup_event():
    """Проверяем доступность Ollama при старте приложения"""
    logger.info("Starting up Mock ML Service...")
    logger.info(f"OLLAMA_HOST environment variable: {OLLAMA_HOST}")

    await asyncio.sleep(5)

    if check_ollama_available(max_retries=10, retry_delay=3):
        app.state.models_ready.set()
        logger.info("Mock ML Service is ready and Ollama is available")
    else:
        logger.warning("Ollama is not available, but service will continue. Requests may fail.")
        app.state.models_ready.set()


@app.get("/")
async def root():
    return {"message": "Mock ML Service is running"}


@app.get("/health")
async def health():
    return await ollama_handlers.health_check(app.state.models_ready)


@app.get("/ping")
async def ping():
    return await ollama_handlers.ping()


@app.get("/ollama/check")
async def check_ollama():
    return await ollama_handlers.check_ollama()


@app.post("/ollama/pull")
async def pull_model(request: Request):
    return await ollama_handlers.pull_model(request)


@app.post("/generate")
async def generate_message(request: Request):
    return await ollama_handlers.generate_message(request)


@app.post("/message_stream")
async def message_stream(request: Request) -> StreamingResponse:
    """Потоковый endpoint для генерации сообщений"""
    models_ready = app.state.models_ready

    if not models_ready.is_set():
        raise HTTPException(status_code=503, detail="Models are still initialising")

    payload: dict[str, Any] = await request.json()
    logger.info(f"Handling /message_stream request with payload: {payload}")

    def event_generator():
        stream = mock_workflow(payload, streaming=True)
        accumulated_content = ""

        for chunk in stream:
            chunk_data = chunk.model_dump_json()
            if chunk.message and chunk.message.content:
                accumulated_content += chunk.message.content
            yield f"data: {chunk_data}\n\n"

        logger.info(
            f"Stream completed. accumulated_content length={len(accumulated_content)}, "
            f"accumulated_content preview={accumulated_content[:100] if accumulated_content else 'empty'}"
        )

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
