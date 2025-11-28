from ml.api.schemas import MessagePayload
from ml.api.schemas.message_payload import Tag


async def workflow_collected(payload: MessagePayload) -> tuple[str, Tag]:
    # TODO: wire to workflow once it's completed

    # TODO: collect workflow
    raise NotImplementedError()


async def workflow(payload: MessagePayload):  # TODO: decide on return type
    # TODO: Implement workflow
    raise NotImplementedError()
