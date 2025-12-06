import logging
from collections.abc import AsyncIterator
from typing import Any

from ollama._types import ChatResponse

from ml.api.schemas import MessagePayload
from ml.api.schemas.message_payload import Tag
from ml.domain.models import GraphState, MetaData
from ml.domain.workflow.agent.pipeline import create_pipeline

logger = logging.getLogger(__name__)


async def workflow_collected(payload: MessagePayload) -> tuple[str, Tag]:
    output_stream, tag = await workflow(payload)

    collected_chunks: list[str] = []

    def append_chunk(chunk_value: str) -> None:
        print(chunk_value, end="")
        collected_chunks.append(chunk_value)

    async for chunk in output_stream:
        if isinstance(chunk, ChatResponse):
            message = chunk.message

            if message is None:
                raise RuntimeError("ChatResponse is missing a message payload")

            thinking = message.thinking
            if thinking is not None:
                if not isinstance(thinking, str):
                    raise TypeError("ChatResponse.message.thinking must be a string when provided")

                append_chunk(thinking)

            content = message.content
            if content is not None:
                if not isinstance(content, str):
                    raise TypeError("ChatResponse.message.content must be a string when provided")

                append_chunk(content)

            continue

        if isinstance(chunk, dict):
            choices = chunk.get("choices")

            if not isinstance(choices, list):
                raise TypeError("Streaming chunk must contain a list of choices")

            for choice in choices:
                if not isinstance(choice, dict):
                    raise TypeError("Each choice in streaming chunk must be a dictionary")

                delta = choice.get("delta")

                if delta is None:
                    raise TypeError("Streaming chunk choice is missing delta data")

                if not isinstance(delta, dict):
                    raise TypeError("Streaming chunk delta must be a dictionary")

                content = delta.get("content")

                if content is None:
                    continue

                if not isinstance(content, str):
                    raise TypeError("Streaming chunk content must be a string when provided")

                append_chunk(content)

            continue

        if isinstance(chunk, str):
            append_chunk(chunk)
            continue

        if isinstance(chunk, bytes):
            append_chunk(chunk.decode("utf-8"))
            continue

        msg = (
            "Workflow output stream yielded unsupported type. "
            f"Expected str, bytes, dict or ChatResponse, got {type(chunk)}"
        )
        raise TypeError(msg)

    collected_response = "".join(collected_chunks)

    return collected_response, tag


async def workflow(payload: MessagePayload) -> tuple[AsyncIterator[dict[str, Any]], Tag]:
    initial_state = GraphState(
        chat_id=payload.chat_id,
        chat=payload.messages,
        user=payload.profile,
        meta=MetaData(is_voice=payload.is_voice, tag=payload.tag),
        model_mode=payload.mode,
        voice_is_valid=None,
        final_prompt=None,
        output_stream=None,
    )

    compiled_pipeline = create_pipeline()

    result_state = await compiled_pipeline.ainvoke(
        initial_state, config={"run_name": "main_pipeline", "recursion_limit": 100}
    )

    validated_state: GraphState

    if isinstance(result_state, GraphState):
        validated_state = result_state
    elif isinstance(result_state, dict):
        validated_state = GraphState.model_validate(result_state)
    else:
        raise TypeError(
            "Workflow pipeline returned an unexpected type: "
            f"{type(result_state)}. Expected GraphState or dict."
        )

    output_stream = validated_state.output_stream
    if output_stream is None:
        raise RuntimeError("Workflow execution completed without producing an output stream")

    if not isinstance(output_stream, AsyncIterator):
        raise TypeError("Workflow output_stream is not an AsyncIterator")

    if not isinstance(validated_state.meta.tag, Tag):
        raise TypeError("Workflow state meta.tag is not a Tag enum value")

    return output_stream, validated_state.meta.tag
