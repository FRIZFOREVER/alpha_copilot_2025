from typing import Iterator

from ml.agent.graph.pipeline import run_pipeline
from ml.configs.message import RequestPayload
from ollama import ChatResponse

def workflow(payload: RequestPayload) -> Iterator[ChatResponse]:
    payload.messages.add_or_change_system(payload.system)
    return run_pipeline(payload)

def workflow_collected(payload: RequestPayload) -> str:
    stream: Iterator[ChatResponse] = workflow(payload=payload)

    buffer_string: str = ''

    for chunk in stream:
        buffer_string.join(chunk.message.content)

    return buffer_string
