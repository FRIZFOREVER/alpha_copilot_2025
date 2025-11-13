from typing import List, Optional
from pydantic import BaseModel, Field
from ml.configs.message import ChatHistory, RequestPayload

class MemoriesEvidance(BaseModel):
    extracted_memories: List[str] = Field(
        default_factory=list,
        description="Contains unverified memories"
    )

class GraphState(BaseModel):
    """State model for LangGraph pipeline."""

    payload: RequestPayload
    memories: MemoriesEvidance = Field(
        default_factory=MemoriesEvidance
    )
    final_prompt: Optional[ChatHistory] = Field(
        default=None,
        description="Field for storing final prompt"
    )