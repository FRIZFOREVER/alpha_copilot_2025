from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from pydantic import BaseModel, ConfigDict, Field

from ml.domain.models.chat_history import ChatHistory
from ml.domain.models.payload_data import MetaData, ModelMode, UserProfile
from ml.domain.models.research import PlannedToolCall, ToolObservation


class GraphState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    chat: ChatHistory
    user: UserProfile
    meta: MetaData
    model_mode: ModelMode
    voice_is_valid: Optional[bool]
    final_prompt: Optional[ChatHistory]
    output_stream: AsyncIterator[dict[str, Any]]
    pending_tool_call: PlannedToolCall | None = None
    last_tool_result: Any | None = None
    observations: list[ToolObservation] = Field(default_factory=list)
