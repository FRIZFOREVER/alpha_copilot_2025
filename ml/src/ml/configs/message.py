from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Dict


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class ChatHistory(BaseModel):
    messages: List[Message] = []

    def add_system(self, content: str) -> Message:
        msg = Message(role=Role.system, content=content)
        self.messages.append(msg)

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