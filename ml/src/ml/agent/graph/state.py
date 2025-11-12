from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from ml.configs.message import Message


class GraphState(BaseModel):
    """State model for LangGraph pipeline."""

    messages: List[Message] = Field(default_factory=list)
    mode: Optional[Literal["research", "fast_answer"]] = None
    thread_id: Optional[str] = None
    checkpoint_namespace: Optional[str] = None
    checkpoint_identifier: Optional[str] = None
    planning_decision: Optional[Dict] = None
    tool_results: List[Dict] = Field(default_factory=list)
    search_history: List[Dict] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    final_answer: Optional[str] = None
    needs_more_research: bool = False
    research_iteration: int = 0
    max_research_iterations: int = 3
    stream_messages: List[Dict[str, str]] = Field(default_factory=list)
    final_prompt_messages: List[Dict[str, str]] = Field(default_factory=list)
    event_log: List[Dict[str, Any]] = Field(default_factory=list)

    def record_event(self, event: str, **details: Any) -> None:
        """Append a structured event entry to ``event_log``."""

        entry: Dict[str, Any] = {"event": event}
        if details:
            entry.update(details)
        self.event_log.append(entry)

