from typing import Any, Dict, Iterator, Optional

from ml.agent.calls.model_calls import make_client, _ReasoningModelClient
from ml.configs.model_config import ModelSettings
from ml.agent.graph.pipeline import run_pipeline_stream
from ollama import ChatResponse

_MODEL_CLIENTS: Dict[str, Any] = {}
_LAST_RESPONSE: Optional[str] = None


def workflow_stream(payload: Dict[str, Any]) -> Iterator[ChatResponse]:
    """Stream workflow responses chunk by chunk."""

    stream = _prepare_workflow_stream(payload)
    buffer: list[str] = []

    for chunk in stream:
        content = _extract_assistant_content(chunk)
        if content is not None:
            buffer.append(content)
        yield chunk

    _record_final_response(buffer)


def workflow_collect(payload: Dict[str, Any]) -> str:
    """Collect workflow response into a single string."""

    stream = _prepare_workflow_stream(payload)
    buffer: list[str] = []

    for chunk in stream:
        content = _extract_assistant_content(chunk)
        if content is not None:
            buffer.append(content)

    final_response = _record_final_response(buffer)

    if final_response:
        return final_response

    return "Извините, не удалось сгенерировать ответ."


def _prepare_workflow_stream(payload: Dict[str, Any]) -> Iterator[ChatResponse]:
    """Prepare the LangGraph workflow stream for the given payload."""

    client: _ReasoningModelClient = _MODEL_CLIENTS["chat"]
    messages = payload.get("messages", [])
    return run_pipeline_stream(client=client, messages=messages)


def _extract_assistant_content(chunk: ChatResponse) -> Optional[str]:
    """Extract assistant message content from a chat chunk when present."""

    message = getattr(chunk, "message", None)
    if message is None:
        return None

    role = getattr(message, "role", None)
    if role != "assistant":
        return None

    content = getattr(message, "content", None)
    if not isinstance(content, str):
        return None

    return content


def _record_final_response(chunks: list[str]) -> Optional[str]:
    """Store the final assistant response assembled from streamed chunks."""

    global _LAST_RESPONSE

    if not chunks:
        _LAST_RESPONSE = None
        return None

    final_answer = "".join(chunks)
    _LAST_RESPONSE = final_answer
    return final_answer


def get_last_response() -> Optional[str]:
    """Return the most recent assembled assistant response, if available."""

    return _LAST_RESPONSE


async def init_models() -> Dict[str, Any]:
    modes = ("chat", "embeddings")
    global _MODEL_CLIENTS
    _MODEL_CLIENTS = {mode: make_client(ModelSettings(api_mode=mode)) for mode in modes}
    return _MODEL_CLIENTS
