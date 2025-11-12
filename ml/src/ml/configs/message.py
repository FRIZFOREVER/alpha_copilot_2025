from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from typing import List, Dict, Optional


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    id: int
    role: Role
    content: str


class ModelMode(str, Enum):
    Fast = "fast"
    Thiking = "thiking"
    Research = "research"
    Auto = "auto"


class RequestPayload(BaseModel):
    messages: List[Message]
    chat_id: Optional[str] = None
    tag: Optional[str] = None
    mode: Optional[ModelMode] = None
    system: Optional[str] = None
    file_url: Optional[str] = None
    is_voice: Optional[bool] = None


class ChatHistory(BaseModel):
    messages: List[Message] = Field(default_factory=list)

    def add_system(self, content: str) -> Message:
        msg = Message(role=Role.system, content=content)
        self.messages.append(msg)
        return msg

    def add_user(self, content: str) -> Message:
        msg = Message(role=Role.user, content=content)
        self.messages.append(msg)
        return msg

    def add_assistant(self, content: str) -> Message:
        msg = Message(role=Role.assistant, content=content)
        self.messages.append(msg)
        return msg

    # Utilities
    def last(self, n: int = 1) -> List[Message]:
        return self.messages[-n:] if n > 0 else []

    def messages_list(self, include_empty: bool = False) -> List[Dict[str, str]]:
        """
        Convert to Ollama's chat format:
        [{"role": "system"|"user"|"assistant", "content": "..."}]
        """
        out: List[Dict[str, str]] = []
        for m in self.messages:
            if not include_empty and not (m.content and m.content.strip()):
                continue
            out.append({"role": m.role.value, "content": m.content or ""})
        return out