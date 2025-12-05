import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from ml.api.schemas import MessagePayload
from ml.domain.workflow.router import workflow

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

    # TODO: websocket client

    logger.info("Invoking workflow for /message_stream request")

    stream = await workflow(payload)

    async def event_generator() -> AsyncIterator[str]:
        async for chunk in stream:
            yield f"data: {json.dumps(chunk)}\n\n"

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


@router.post("/message")
async def message(payload: MessagePayload):
    # TODO: error 503 on init handling

    # TODO: workflow_collected calling

    raise NotImplementedError()
