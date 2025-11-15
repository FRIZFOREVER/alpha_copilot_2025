from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    id: int | None = None
    role: Role
    content: str


class ChatHistory(BaseModel):
    messages: list[Message] = Field(default_factory=list)

    # TODO: Implement overrides for add functions when input is Message class
    # instead of content. Validate it on role as well
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

    def last_message_as_history(self) -> ChatHistory:
        history: ChatHistory = ChatHistory()
        history.add_user(self.messages[-1].content)
        return history

    def messages_list(self) -> list[dict[str, str]]:
        return [{"role": msg.role.value, "content": msg.content} for msg in self.messages]

    def model_dump_string(self) -> str:
        return "\n\n".join(f"{msg.role.value}: {msg.content}" for msg in self.messages)


class ModelMode(str, Enum):
    Fast = "fast"
    Thiking = "thinking"
    Research = "research"
    Auto = "auto"


class Tag(str, Enum):
    General = "general"
    Finance = "finance"
    Law = "law"
    Marketing = "marketing"
    Management = "management"


class Profile(BaseModel):
    id: int
    login: str
    username: str
    user_info: str
    business_info: str
    additional_instructions: str


class RequestPayload(BaseModel):
    messages: ChatHistory
    chat_id: str
    tag: Tag | None = None
    mode: ModelMode
    system: str
    file_url: str
    is_voice: bool
    profile: Profile

    @field_validator("messages", mode="before")
    @classmethod
    def normalize_messages(cls, message_list):
        return {"messages": message_list}

    @field_validator("tag", mode="before")
    @classmethod
    def replace_tag(cls, v):
        if v == "":
            return None
        return v
