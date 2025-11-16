import logging
from enum import Enum

from ml.agent.graph.state import (
    GraphState,
    NextAction,
    ResearchToolRequest,
    ResearchTurn,
)
from ml.agent.prompts import get_research_reason_prompt
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ResearchReactAction(str, Enum):
    THINK = "think"
    TOOL = "tool"
    FINALIZE = "finalize"


class ResearchReactResponse(BaseModel):
    thought: str = Field(description="Scratchpad reasoning for the current step")
    action: ResearchReactAction = Field(
        description="Directive emitted by the model for how to proceed"
    )
    tool_name: str | None = Field(
        default=None,
        description="Identifier for the tool to execute when action requests it",
    )
    query: str | None = Field(
        default=None,
        description="Primary query or payload that should be sent to the tool",
    )
    comparison_text: str | None = Field(
        default=None,
        description=(
            "Optional additional instructions for comparing or validating tool output"
        ),
    )
    final_answer: str | None = Field(
        default=None,
        description="Completed response to return to the user when finalizing",
    )


def research_react_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    prompt: ChatHistory = get_research_reason_prompt(
        conversation=state.payload.messages,
        turn_history=state.turn_history,
        latest_reasoning=state.latest_reasoning,
    )

    response = client.call_structured(
        messages=prompt,
        output_schema=ResearchReactResponse,
    )

    state.loop_counter = state.loop_counter + 1
    state.latest_reasoning = response.thought

    # Логирование reasoning
    if (
        state.graph_log_client
        and state.question_id
        and state.payload.tag
        and state.graph_log_loop
    ):
        try:
            # Используем event loop для отправки лога
            state.graph_log_loop.run_until_complete(
                state.graph_log_client.send_log(
                    tag=state.payload.tag.value,
                    question_id=state.question_id,
                    message=f"Research React - Reasoning: {response.thought[:500]}",
                )
            )
        except Exception as e:
            logger.warning(f"Ошибка отправки graph_log: {e}")

    turn = ResearchTurn(reasoning_summary=response.thought)

    if response.action == ResearchReactAction.TOOL:
        metadata: dict[str, str] = {}
        if response.comparison_text is not None:
            metadata["comparison_text"] = response.comparison_text

        tool_request = ResearchToolRequest(
            tool_name=response.tool_name or "",
            input_text=response.query or "",
            metadata=metadata,
        )
        turn.request = tool_request
        state.active_tool_request = tool_request
        state.next_action = NextAction.REQUEST_TOOL
    elif response.action == ResearchReactAction.FINALIZE:
        final_prompt = ChatHistory()
        final_prompt.add_or_change_system(state.payload.system)
        final_prompt.add_assistant(response.final_answer or "")
        state.final_prompt = final_prompt
        state.active_tool_request = None
        state.next_action = NextAction.FINISH
    else:
        state.active_tool_request = None
        state.next_action = NextAction.THINK

    state.turn_history.append(turn)
    return state
