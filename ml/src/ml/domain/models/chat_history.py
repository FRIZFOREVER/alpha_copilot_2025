from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, List, overload

from pydantic import BaseModel, model_validator

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """
    Chat actor type:

    - "system"
    - "user"
    - "assistant"
    """

    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    """
    Chat message

    id: Optional identifier if it's linked to a message in Postgres db
    role: "system" | "user" | "assistant"
    """

    id: int | None = None
    role: Role
    content: str

    @model_validator(mode="after")
    def id_validation(self) -> Message:
        """
        Validator for usage: system message must never have id
        """
        if self.role is Role.system and self.id is not None:
            logger.error("System messages must not have an id (id must be None).")
            raise ValueError("System messages must not have an id (id must be None).")

        return self


class ChatHistory(BaseModel):
    """
    Ordered sequence of chat messages.

    messages: list of Message typed objects

    constraints:
    - no consecutive user or assistant messages
    - single system message per ChatHistory
    - no id for system message
    """

    messages: list[Message]

    @model_validator(mode="after")
    def validate_turn_order(self) -> ChatHistory:
        last_non_system: Role | None = None

        for msg in self.messages:
            if msg.role is Role.system:
                continue

            if last_non_system is not None and msg.role is last_non_system:
                logger.error("Invalid chat history provided: consecutive non-system messages found")
                raise ValueError(
                    "Invalid chat history: consecutive non-system messages "
                    f"with the same role '{msg.role.value}'. "
                    "User and assistant messages must alternate."
                )
            last_non_system = msg.role

        return self

    @overload
    def add_or_change_system(self, arg: str) -> None: ...
    @overload
    def add_or_change_system(self, arg: Message) -> None: ...

    def add_or_change_system(self, arg: str | Message) -> None:
        """
        Deletes current user_message and inserts new one in start of chat history
        """
        self.messages = [msg for msg in self.messages if msg.role != Role.system]
        if isinstance(arg, Message):
            self.messages.insert(0, arg)
            return
        else:
            system_message: Message = Message(role=Role.system, content=arg)
            self.messages.insert(0, system_message)
            return

    @overload
    def add_user(self, arg: str) -> None: ...
    @overload
    def add_user(self, arg: Message) -> None: ...

    def add_user(self, arg: str | Message) -> None:
        if self.messages:
            if self.last_message(ensure_user=False).role == Role.user:
                raise RuntimeError("Tried to assign 2 consecutive user messages in a row")

        if isinstance(arg, Message):
            self.messages.append(arg)
            return

        else:
            user_message: Message = Message(role=Role.user, content=arg)
            self.messages.append(user_message)
            return

    @overload
    def add_assistant(self, arg: str) -> None: ...
    @overload
    def add_assistant(self, arg: Message) -> None: ...

    def add_assistant(self, arg: str | Message) -> None:
        if self.messages:
            if self.last_message(ensure_user=False).role == Role.assistant:
                raise RuntimeError("Tried to assign 2 consecutive assistant messages in a row")

        if isinstance(arg, Message):
            self.messages.append(arg)
            return

        else:
            user_message: Message = Message(role=Role.assistant, content=arg)
            self.messages.append(user_message)
            return

    # TODO: dumping chat history as a string function
    def model_dump_string(self) -> str:
        raise NotImplementedError("Function not implemented yet")

    def last_message(self, *, ensure_user: bool = True) -> Message:
        if not self.messages:
            raise RuntimeError("Tried to call last_user_request from empty ChatHistory")
        last_message: Message = self.messages[-1]
        if ensure_user and last_message.role != Role.user:
            raise ValueError("Last message in chat history is not user message")
        return last_message

    def model_dump_chat(self) -> List[Dict[str, str]]:
        return [
            {"role": message.role.value, "content": message.content} for message in self.messages
        ]
