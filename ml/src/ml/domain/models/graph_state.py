from typing import Any, AsyncIterator, Optional

from pydantic import BaseModel

from ml.domain.models.chat_history import ChatHistory
from ml.domain.models.payload_data import MetaData, ModelMode, UserProfile


class GraphState(BaseModel):
    chat: ChatHistory
    user: UserProfile
    meta: MetaData
    model_mode: ModelMode
    voice_is_valid: Optional[bool]
    final_prompt: Optional[ChatHistory]
    output_stream: AsyncIterator[dict[str, Any]]
