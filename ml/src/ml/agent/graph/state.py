from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from ml.configs.message import Message


class GraphState(BaseModel):
    """State model for LangGraph pipeline."""

    messages: List[Message] = Field(default_factory=list)
    mode: Optional[Literal["research", "fast_answer"]] = None
    planning_decision: Optional[Dict] = None
    tool_results: List[Dict] = Field(default_factory=list)
    search_history: List[Dict] = Field(default_factory=list)
    final_answer: Optional[str] = None
    needs_more_research: bool = False
    research_iteration: int = 0
    max_research_iterations: int = 3
    stream_messages: List[Dict[str, str]] = Field(default_factory=list)

