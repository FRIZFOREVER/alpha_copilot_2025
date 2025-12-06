import json
import logging
from collections.abc import AsyncIterator
from typing import Union

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from ollama._types import ChatResponse

from ml.api.schemas import MessagePayload
from ml.api.external import GraphLogWebSocketClient
from ml.domain.workflow.router import workflow, workflow_collected

router = APIRouter(tags=["workflow"])

logger = logging.getLogger(__name__)


@router.post("/message_stream")
async def message_stream(request: Request, payload: MessagePayload) -> StreamingResponse:
    model_ready = request.app.state.model_ready
    if not model_ready.is_set():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models are still initialising",
        )

    graph_log_client = request.app.state.graph_log_client
    if not isinstance(graph_log_client, GraphLogWebSocketClient):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Graph log client is not configured",
        )

    logger.info("Connecting graph log websocket for chat_id=%s", payload.chat_id)
    try:
        await graph_log_client.connect(payload.chat_id)
    except Exception as exc:
        logger.exception("Failed to initialise graph log websocket connection")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Graph log websocket connection failed",
        ) from exc

    logger.info("Invoking workflow for /message_stream request")

    stream, tag, file_url = await workflow(payload)

    if file_url is not None and not isinstance(file_url, str):
        raise TypeError("Workflow file_url must be a string or None")

    async def event_generator() -> AsyncIterator[Union[str, bytes]]:
        try:
            async for chunk in stream:
                if isinstance(chunk, ChatResponse):
                    chunk_payload = chunk.model_dump_json()
                    yield f"data: {chunk_payload}\n\n"
                    continue

                if isinstance(chunk, dict):
                    chunk_payload = json.dumps(chunk, ensure_ascii=False)
                    yield f"data: {chunk_payload}\n\n"
                    continue

                if isinstance(chunk, str):
                    yield f"data: {chunk}\n\n"
                    continue

                if isinstance(chunk, bytes):
                    yield b"data: " + chunk + b"\n\n"
                    continue

                msg = (
                    "Workflow output stream yielded unsupported type. "
                    f"Expected str, bytes, dict or ChatResponse, got {type(chunk)}"
                )
                logger.error(msg)
                raise TypeError(msg)

            final_file_url = None if file_url == "" else file_url

            final_chunk_payload = json.dumps({"file_url": final_file_url}, ensure_ascii=False)
            yield f"data: {final_chunk_payload}\n\n"
        finally:
            await graph_log_client.close(payload.chat_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Tag": tag.value,
        },
    )


@router.post("/message")
async def message(request: Request, payload: MessagePayload) -> JSONResponse:
    model_ready = request.app.state.model_ready
    if not model_ready.is_set():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models are still initialising",
        )

    graph_log_client = request.app.state.graph_log_client
    if not isinstance(graph_log_client, GraphLogWebSocketClient):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Graph log client is not configured",
        )

    logger.info("Connecting graph log websocket for chat_id=%s", payload.chat_id)
    try:
        await graph_log_client.connect(payload.chat_id)
    except Exception as exc:
        logger.exception("Failed to initialise graph log websocket connection")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Graph log websocket connection failed",
        ) from exc

    logger.info("Invoking workflow for /message request")

    try:
        collected_response, tag = await workflow_collected(payload)
    finally:
        await graph_log_client.close(payload.chat_id)

    return JSONResponse(content={"content": collected_response, "tag": tag.value})
