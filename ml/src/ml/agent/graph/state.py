from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from ml.configs.message import ChatHistory, ModelMode



class GraphState(BaseModel):
    """State model for LangGraph pipeline."""

    messages: ChatHistory
    mode: ModelMode