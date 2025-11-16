import logging
from enum import Enum

from pydantic import BaseModel, Field

from ml.agent.graph.state import (
    GraphState,
    NextAction,
    ResearchToolRequest,
    ResearchTurn,
)
from ml.agent.prompts import get_research_reason_prompt
from ml.agent.tools.registry import get_tool_registry
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory

logger: logging.Logger = logging.getLogger(__name__)


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
        description=("Optional additional instructions for comparing or validating tool output"),
    )
    final_answer: str | None = Field(
        default=None,
        description="Completed response to return to the user when finalizing",
    )


def research_react_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Research react node")
    available_tools = list(get_tool_registry().values())
    prompt: ChatHistory = get_research_reason_prompt(
        profile=state.payload.profile,
        conversation=state.payload.messages,
        turn_history=state.turn_history,
        latest_reasoning=state.latest_reasoning,
        available_tools=available_tools,
    )

    response = client.call_structured(
        messages=prompt,
        output_schema=ResearchReactResponse,
    )

    logger.info("Research react reasoning: %s", response.thought)

    state.loop_counter = state.loop_counter + 1
    state.latest_reasoning = response.thought

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
        state.active_tool_request = None
        state.next_action = NextAction.ANSWER
    else:
        state.active_tool_request = None
        state.next_action = NextAction.THINK

    state.turn_history.append(turn)
    return state
