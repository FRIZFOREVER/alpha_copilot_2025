import asyncio
import logging
from collections.abc import Iterator
from contextlib import AsyncExitStack, asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from ollama import ChatResponse
from starlette.types import Send

from ml.agent.router import workflow_async, workflow_collected_async
from ml.api.graph_history import GraphLogClient, get_backend_url
from ml.api.graph_logging import (
    GraphLogContext,
    GraphLogDispatcher,
    reset_graph_log_context,
    set_graph_log_context,
)
from ml.api.ollama_setup import (
    download_missing_models,
    fetch_available_models,
    fetch_running_models,
    get_models_from_env,
    init_models,
    warmup_models,
)
from ml.configs.message import RequestPayload, Tag
from ml.configs.types import ModelClients

logger: logging.Logger = logging.getLogger(__name__)


class ChatResponseEventStream(StreamingResponse):
    media_type = "text/event-stream"

    def __init__(self, content: Iterator[ChatResponse], headers: dict[str, Any]) -> None:
        super().__init__(content, media_type=self.media_type, headers=headers)

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        async for chunk in self.body_iterator:
            await send(
                {
                    "type": "http.response.body",
                    "body": self._serialize_chunk(chunk),
                    "more_body": True,
                }
            )
        await send({"type": "http.response.body", "body": b"", "more_body": False})

    def _serialize_chunk(self, chunk: Any) -> bytes:
        if isinstance(chunk, (bytes, bytearray)):
            return bytes(chunk)
        if isinstance(chunk, memoryview):
            return chunk.tobytes()
        if isinstance(chunk, str):
            return chunk.encode(self.charset or "utf-8")
        if isinstance(chunk, ChatResponse):
            return f"data: {chunk.model_dump_json()}\n\n".encode()
        raise TypeError(f"Unsupported chunk type: {type(chunk)!r}")


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/message")
    async def message(payload: RequestPayload) -> JSONResponse:  # type: ignore[reportUnusedFunction]
        # Check if models are initialized
        if not app.state.models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        message_text: str
        tag: Tag
        try:
            message_text, tag = await workflow_collected_async(payload)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response from collect workflow",
            ) from exc

        return JSONResponse(content={"message": message_text}, headers={"Tag": tag.value})

    @app.post("/message_stream")
    async def message_stream(payload: RequestPayload) -> StreamingResponse:  # type: ignore[reportUnusedFunction]
        # Check if models are initialized
        if not app.state.models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        backend_url = get_backend_url()
        exit_stack = AsyncExitStack()
        dispatcher: GraphLogDispatcher | None = None
        dispatcher_task: asyncio.Task[None] | None = None
        previous_graph_log_context: GraphLogContext | None = None
        graph_log_context_active = False

        def _reset_graph_log_context() -> None:
            nonlocal graph_log_context_active
            if graph_log_context_active:
                reset_graph_log_context(previous_graph_log_context)
                graph_log_context_active = False

        try:
            client = await exit_stack.enter_async_context(
                GraphLogClient(backend_url=backend_url, chat_id=payload.chat_id)
            )
            loop = asyncio.get_running_loop()
            dispatcher = GraphLogDispatcher(loop=loop, client=client)
            dispatcher_task = asyncio.create_task(dispatcher.run())
            previous_graph_log_context = set_graph_log_context(
                dispatcher=dispatcher, answer_id=payload.messages.get_answer_id()
            )
            graph_log_context_active = True

            stream, tag = await workflow_async(payload)
        except HTTPException:
            _reset_graph_log_context()
            if dispatcher:
                dispatcher.stop()
            if dispatcher_task:
                with suppress(Exception):
                    await dispatcher_task
            with suppress(Exception):
                await exit_stack.aclose()
            raise
        except Exception as exc:
            _reset_graph_log_context()
            if dispatcher:
                dispatcher.stop()
            if dispatcher_task:
                with suppress(Exception):
                    await dispatcher_task
            with suppress(Exception):
                await exit_stack.aclose()
            logger.exception("Failed to start streaming workflow")
            raise HTTPException(
                status_code=500, detail="Failed to start streaming workflow"
            ) from exc

        cleanup_scheduled = False

        async def _async_cleanup() -> None:
            if dispatcher:
                dispatcher.stop()
            if dispatcher_task:
                with suppress(Exception):
                    await dispatcher_task
            _reset_graph_log_context()
            with suppress(Exception):
                await exit_stack.aclose()

        def _schedule_cleanup() -> None:
            nonlocal cleanup_scheduled
            if cleanup_scheduled:
                return
            cleanup_scheduled = True
            asyncio.run_coroutine_threadsafe(_async_cleanup(), loop).result()

        def event_generator() -> Iterator[ChatResponse]:
            try:
                for chunk in stream:
                    yield chunk
            except Exception as exc:
                _schedule_cleanup()
                raise HTTPException(status_code=500, detail="Streaming workflow failed") from exc
            finally:
                if close_stream:
                    with suppress(Exception):
                        close_stream()
                _schedule_cleanup()

        headers: dict[str, Any] = {"tag": tag.value}
        return ChatResponseEventStream(event_generator(), headers=headers)

    @app.get("/ping")
    async def ping() -> dict[str, str]:  # type: ignore[reportUnusedFunction]
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
    async def healthcheck() -> dict[str, str]:  # type: ignore[reportUnusedFunction]
        return {"status": "healthy"}

    return app
