import asyncio
from collections.abc import Iterator

from ollama import ChatResponse

from ml.agent.graph.pipeline import run_pipeline
from ml.configs.message import RequestPayload, Tag


def workflow(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
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


async def workflow_async(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
    return await asyncio.to_thread(workflow, payload)


async def workflow_collected_async(payload: RequestPayload) -> tuple[str, Tag]:
    return await asyncio.to_thread(workflow_collected, payload)
