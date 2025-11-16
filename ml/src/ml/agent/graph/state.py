from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ml.configs.message import ChatHistory, RequestPayload


class MemoriesEvidance(BaseModel):
    extracted_memories: list[str] = Field(
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
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured argument dictionary prepared for the tool",
    )
    metadata: dict[str, Any] = Field(
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
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Auxiliary details that help interpret the observation",
    )


class ResearchTurn(BaseModel):
    request: ResearchToolRequest | None = Field(
        default=None,
        description="Tool request issued during this turn, if any",
    )
    observation: ResearchObservation | None = Field(
        default=None,
        description="Observation returned for the issued request",
    )
    reasoning_summary: str | None = Field(
        default=None,
        description="Short summary of why the agent took this turn",
    )


class PlannerToolExecution(BaseModel):
    tool_name: str = Field(
        description="Name of the tool that was executed by the planner",
    )
    arguments: dict[str, str] = Field(
        default_factory=dict,
        description="Arguments that were forwarded to the tool",
    )
    success: bool = Field(
        default=False,
        description="Indicator showing whether the tool call succeeded",
    )
    output_preview: str = Field(
        default="",
        description="Short textual summary of the tool output or error",
    )


class GraphState(BaseModel):
    """State model for LangGraph pipeline."""

    payload: RequestPayload
    memories: MemoriesEvidance = Field(
        default_factory=MemoriesEvidance,
    )
    final_prompt: ChatHistory | None = Field(
        default=None,
        description="Field for storing final prompt",
    )
    final_answer_draft: str | None = Field(
        default=None,
        description="Draft of the final assistant answer before formatting",
    )
    final_answer_evidence: list[str] = Field(
        default_factory=list,
        description=("Evidence snippets or references collected during reasoning"),
    )
    thinking_plan_summary: str | None = Field(
        default=None,
        description="High-level recap of the thinking planner strategy",
    )
    thinking_plan_steps: list[str] = Field(
        default_factory=list,
        description="Ordered list of planner steps produced by the model",
    )
    thinking_tool_executions: list[PlannerToolExecution] = Field(
        default_factory=list,
        description="Detailed record of each tool call performed by the planner",
    )
    thinking_evidence: list[str] = Field(
        default_factory=list,
        description="Evidence items gathered directly by the thinking planner",
    )
    turn_history: list[ResearchTurn] = Field(
        default_factory=list,
        description="Chronological record of reasoning, tool calls, and observations",
    )
    active_tool_request: ResearchToolRequest | None = Field(
        default=None,
        description="Tool request being prepared for execution in the current step",
    )
    active_observation: ResearchObservation | None = Field(
        default=None,
        description="Latest observation received from an external tool",
    )
    latest_reasoning_text: str | None = Field(
        default=None,
        description="Latest reasoning summary emitted by the agent",
    )
    next_action: NextAction = Field(
        default=NextAction.THINK,
        description="Routing hint that indicates how downstream nodes should proceed",
    )
