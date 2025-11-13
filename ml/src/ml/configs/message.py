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


class ChatHistory(BaseModel):
    messages: List[Message] = Field(default_factory=list)

    # TODO: Implement overrides for add functions when input is Message class instead of content. Validate it on role as well
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

    def last_message_as_history(self) -> Message:
        return ChatHistory().add_user(self.messages[-1])
      
    def messages_list(self) -> List[Dict[str, str]]:
        return [{"role": msg.role.value, "content": msg.content} for msg in self.messages]


class RequestPayload(BaseModel):
    messages: ChatHistory
    chat_id: str
    tag: str
    mode: ModelMode
    system: str
    file_url: str
    is_voice: bool
