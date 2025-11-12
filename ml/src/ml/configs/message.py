from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from typing import List, Dict, Optional


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    id: Optional[int] = Field(default=None)
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

    def add_or_change_system(self, content: str) -> Message:
        self.messages = [msg for msg in self.messages if msg.role != Role.system]
        system_message = Message(role=Role.system, content=content)
        self.messages.insert(0, system_message)
        return system_message

    def add_user(self, content: str) -> Message:
        msg = Message(role=Role.user, content=content)
        self.messages.append(msg)
        return msg

    def add_assistant(self, content: str) -> Message:
        msg = Message(role=Role.assistant, content=content)
        self.messages.append(msg)
        return msg

    def messages_list(self) -> List[Dict[str, str]]:
        return [{"role": msg.role.value, "content": msg.content} for msg in self.messages]