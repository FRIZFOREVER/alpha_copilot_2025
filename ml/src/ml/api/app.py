import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from ml.agent.router import (
    STREAM_COMPLETE,
    AsyncStreamHandle,
    StreamError,
    async_stream_workflow,
    workflow_collected_async,
)
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


def _drain_async_queue(queue: asyncio.Queue[Any]) -> None:
    while True:
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            break


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
        stream_handle: AsyncStreamHandle
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

            stream_handle = await async_stream_workflow(payload)
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

        async def event_generator() -> AsyncIterator[str]:
            try:
                while True:
                    item = await stream_handle.queue.get()
                    if item is STREAM_COMPLETE:
                        break
                    if isinstance(item, StreamError):
                        raise HTTPException(
                            status_code=500, detail="Streaming workflow failed"
                        ) from item.error
                    yield f"data: {item.model_dump_json()}\n\n"
            except asyncio.CancelledError:
                raise
            finally:
                stream_handle.stop()
                _drain_async_queue(stream_handle.queue)
                with suppress(Exception):
                    await stream_handle.worker_task
                if dispatcher:
                    dispatcher.stop()
                if dispatcher_task:
                    with suppress(Exception):
                        await dispatcher_task
                _reset_graph_log_context()
                with suppress(Exception):
                    await exit_stack.aclose()

        headers: dict[str, Any] = {"tag": stream_handle.tag.value}
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers=headers,
        )

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
