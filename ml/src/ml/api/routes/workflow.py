import logging
from collections.abc import AsyncIterator
from typing import Union

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

    stream = workflow(payload)

    async def event_generator() -> AsyncIterator[Union[str, bytes]]:
        async for chunk in stream:
            if not isinstance(chunk, (str, bytes)):
                msg = (
                    "Workflow output stream yielded unsupported type. "
                    f"Expected str or bytes, got {type(chunk)}"
                )
                logger.error(msg)
                raise TypeError(msg)

            yield chunk

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
