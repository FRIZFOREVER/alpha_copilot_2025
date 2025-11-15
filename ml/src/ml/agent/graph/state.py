from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ml.configs.message import ChatHistory, RequestPayload


class MemoriesEvidance(BaseModel):
    extracted_memories: List[str] = Field(
        default_factory=list,
        description="Contains unverified memories",
    )


class NextAction(str, Enum):
    THINK = "think"
    REQUEST_TOOL = "request_tool"
    AWAIT_OBSERVATION = "await_observation"
    ANSWER = "answer"
    FINISH = "finish"


class ResearchToolRequest(BaseModel):
    tool_name: str = Field(
        description="Identifier of the tool the agent would like to use",
    )
    input_text: str = Field(
        default="",
        description="Raw input or prompt that should be forwarded to the tool",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extra structured context for the downstream tool",
    )


class ResearchObservation(BaseModel):
    tool_name: str = Field(
        description="Name of the tool that produced this observation",
    )
    content: str = Field(
        description="Resulting content or evidence gathered from the tool",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Auxiliary details that help interpret the observation",
    )


class ResearchTurn(BaseModel):
    request: Optional[ResearchToolRequest] = Field(
        default=None,
        description="Tool request issued during this turn, if any",
    )
    observation: Optional[ResearchObservation] = Field(
        default=None,
        description="Observation returned for the issued request",
    )
    reasoning_summary: Optional[str] = Field(
        default=None,
        description="Short summary of why the agent took this turn",
    )


class GraphState(BaseModel):
    """State model for LangGraph pipeline."""

    payload: RequestPayload
    memories: MemoriesEvidance = Field(
        default_factory=MemoriesEvidance,
    )
    final_prompt: Optional[ChatHistory] = Field(
        default=None,
        description="Field for storing final prompt",
    )
    final_answer_draft: Optional[str] = Field(
        default=None,
        description="Draft of the final assistant answer before formatting",
    )
    final_answer_evidence: List[str] = Field(
        default_factory=list,
        description=(
            "Evidence snippets or references collected during reasoning"
        ),
    )
    turn_history: List[ResearchTurn] = Field(
        default_factory=list,
        description="Chronological record of reasoning, tool calls, and observations",
    )
    active_tool_request: Optional[ResearchToolRequest] = Field(
        default=None,
        description="Tool request being prepared for execution in the current step",
    )
    active_observation: Optional[ResearchObservation] = Field(
        default=None,
        description="Latest observation received from an external tool",
    )
    latest_reasoning: Optional[str] = Field(
        default=None,
        description="Latest reasoning summary emitted by the agent",
    )
    loop_counter: int = Field(
        default=0,
        description=(
            "Monotonic counter incremented by each graph iteration. "
            "Nodes should compare this value against their configured maximum "
            "iterations to prevent unbounded loops."
        ),
    )
    next_action: NextAction = Field(
        default=NextAction.THINK,
        description="Routing hint that indicates how downstream nodes should proceed",
    )
