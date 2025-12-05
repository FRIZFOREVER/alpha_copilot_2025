from collections.abc import AsyncIterator
from typing import Any

from ml.api.schemas import MessagePayload
from ml.api.schemas.message_payload import Tag
from ml.domain.models import GraphState, MetaData
from ml.domain.workflow.agent.pipeline import create_pipeline


async def workflow_collected(payload: MessagePayload) -> tuple[str, Tag]:
    # TODO: wire to workflow once it's completed

    # TODO: collect workflow
    raise NotImplementedError()


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
