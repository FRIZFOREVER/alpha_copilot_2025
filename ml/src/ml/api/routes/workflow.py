from fastapi import APIRouter

from ml.api.schemas import MessagePayload

router = APIRouter(tags=["workflow"])


@router.post("/message_stream")
async def message_stream(payload: MessagePayload):
    # TODO: error 503 on init handling

    # TODO: websocket client

    # TODO: workflow calling

    # TODO: output streaming

    raise NotImplementedError()


@router.post("/message")
async def message(payload: MessagePayload):
    # TODO: error 503 on init handling

    # TODO: workflow_collected calling

    raise NotImplementedError()
