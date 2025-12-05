
from __future__ import annotations

from typing import Any, AsyncIterator, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ml.domain.models.chat_history import ChatHistory
from ml.domain.models.payload_data import MetaData, ModelMode, UserProfile
from ml.domain.models.research import PlannedToolCall
from ml.domain.models.tools_data import Evidence, ToolCall, ToolResult


class GraphState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # general data
    chat: ChatHistory
    user: UserProfile
    meta: MetaData

    # validational fields
    model_mode: ModelMode
    voice_is_valid: Optional[bool]

    # results
    final_prompt: Optional[ChatHistory]
    output_stream: Optional[AsyncIterator[dict[str, Any]]]

    # thinking related
    planned_tool_call: Optional[PlannedToolCall] = None
    pending_tool_call: Optional[ToolCall] = None
    last_tool_result: Optional[ToolResult] = None
    last_executed_tool: Optional[str] = None
    evidence_list: List[Evidence] = Field(default_factory=list)
    tool_call_history: List[ToolCall] = Field(default_factory=list)
