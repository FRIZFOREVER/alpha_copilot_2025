from collections.abc import AsyncIterator

import pytest

from ml.domain.models import (
    ChatHistory,
    GraphState,
    Message,
    MetaData,
    ModelMode,
    Role,
    Tag,
    UserProfile,
)
from ml.domain.workflow.agent.conditionals import research_decision
from ml.domain.workflow.agent.nodes import (
    research_answer,
    research_observer,
    research_reason,
    research_tool_call,
)


async def _empty_stream() -> AsyncIterator[dict[str, str]]:
    if False:
        yield {}


def _build_state() -> GraphState:
    chat = ChatHistory(messages=[Message(id=1, role=Role.user, content="Find AI news")])

    return GraphState(
        chat_id=1,
        chat=chat,
        user=UserProfile(
            id=1,
            login="user",
            username="Test User",
            user_info="",
            business_info="",
            additional_instructions="",
        ),
        meta=MetaData(is_voice=False, tag=Tag.General),
        file_url=None,
        model_mode=ModelMode.Research,
        voice_is_valid=None,
        final_prompt=None,
        output_stream=_empty_stream(),
    )


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio("asyncio")
async def test_research_cycle_runs_two_iterations() -> None:
    state = _build_state()

    state = await research_reason(state)
    assert state.pending_tool_call is not None
    assert research_decision(state) == "tool_call"

    state = research_tool_call(state)
    assert state.last_tool_result is not None

    state = research_observer(state)
    assert len(state.observations) == 1
    assert state.pending_tool_call is None
    assert state.last_tool_result is None

    state = await research_reason(state)
    assert state.pending_tool_call is not None

    state = research_tool_call(state)
    state = research_observer(state)
    assert len(state.observations) == 2

    state = await research_reason(state)
    assert state.pending_tool_call is None
    assert research_decision(state) == "finalize"

    state = research_answer(state)
    assert state.final_prompt is not None
    assert "Research observations" in state.final_prompt.messages[-1].content
    assert "Find AI news" in state.final_prompt.messages[-1].content
