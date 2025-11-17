from __future__ import annotations

import logging
from enum import Enum

from pydantic import BaseModel, Field, field_validator

logger: logging.Logger = logging.getLogger(__name__)


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    id: int | None = None
    role: Role
    content: str


def _empty_messages() -> list[Message]:
    return []


class ChatHistory(BaseModel):
    messages: list[Message] = Field(default_factory=_empty_messages)

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

    def get_answer_id(self) -> int:
        id: int | None = self.messages[-1].id
        if id:
            return id
        else:
            logger.error("last user message ID is none, which is impossible")
            raise RuntimeError("last user message ID is none, which is impossible")


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


class UserProfile(BaseModel):
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
    mode: ModelMode | str | None = Field(default=ModelMode.Auto)
    file_url: str
    is_voice: bool
    profile: UserProfile

    @field_validator("messages", mode="before")
    @classmethod
    def normalize_messages(cls, message_list: list[Message]) -> dict[str, list[Message]]:
        if message_list:
            return {"messages": message_list}
        else:
            logger.exception("Found no messages inside payload")
            raise RuntimeError("Expected messages inside payload, got none")

    @field_validator("tag", mode="before")
    @classmethod
    def replace_tag(cls, v: Tag | str | None) -> Tag | None:
        if v is None:
            return None

        elif v == "":
            return None

        if isinstance(v, Tag):
            return v

        try:
            return Tag(v)
        except ValueError as exc:
            logger.exception("Found invalid tag inside payload: %s", v)
            raise RuntimeError("Expected a valid Tag value") from exc

    @field_validator("mode", mode="before")
    @classmethod
    def validate_mode(cls, v: ModelMode | str | None) -> ModelMode:
        if v is None:
            return ModelMode.Auto

        if isinstance(v, ModelMode):
            return v

        if isinstance(v, str):
            try:
                return ModelMode(v)
            except ValueError:
                return ModelMode.Auto

        logger.exception("Found invalid mode inside payload: %s", v)
        raise RuntimeError("Expected a valid ModelMode value")
