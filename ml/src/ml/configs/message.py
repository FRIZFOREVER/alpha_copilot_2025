from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Optional


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    id: Optional[int] = None
    role: Role
    content: str


class ModelMode(str, Enum):
    Fast = "fast"
    Thiking = "thiking"
    Research = "research"
    Auto = "auto"


class RequestPayload(BaseModel):
    messages: List[Message]
    chat_id: str
    tag: str
    mode: ModelMode
    system: str
    file_url: str
    is_voice: bool


class ChatHistory(BaseModel):
    messages: List[Message] = Field(default_factory=list)

    def add_or_change_system(self, content: str) -> None:
        self.messages = [msg for msg in self.messages if msg.role != Role.system]
        system_message = Message(role=Role.system, content=content)
        self.messages.insert(0, system_message)
        return

    def add_user(self, content: str) -> None:
        msg = Message(role=Role.user, content=content)
        self.messages.append(msg)
        return

    def add_assistant(self, content: str) -> None:
        msg = Message(role=Role.assistant, content=content)
        self.messages.append(msg)
        return

    def messages_list(self) -> List[Dict[str, str]]:
        return [{"role": msg.role.value, "content": msg.content} for msg in self.messages]