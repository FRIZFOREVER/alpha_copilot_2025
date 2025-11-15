from collections.abc import Iterator

from ollama import ChatResponse

from ml.agent.graph.pipeline import run_pipeline
from ml.configs.message import RequestPayload, Tag


def workflow(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
    # TODO: Change when payload becomes valid with personalisation
    payload.messages.add_or_change_system(payload.system)
    return run_pipeline(payload)


def workflow_collected(payload: RequestPayload) -> tuple[str, Tag]:
    tag: Tag
    stream: Iterator[ChatResponse]
    stream, tag = workflow(payload=payload)

    buffer_string: str = ""

    for chunk in stream:
        content: str | None = chunk.message.content
        if content:
            buffer_string += content

    return buffer_string, tag
