"""Pydantic схемы для запросов и ответов"""

from pydantic import BaseModel


class Message(BaseModel):
    role: str = "assistant"
    content: str = ""
    thinking: str | None = None
    images: str | None = None
    tool_name: str | None = None
    tool_calls: str | None = None


class StreamChunk(BaseModel):
    model: str = "qwen3:0.6b"
    created_at: str = None
    done: bool = False
    done_reason: str | None = None
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None
    message: Message = None


class TelegramAuthStartRequest(BaseModel):
    user_id: str
    phone_number: str


class TelegramAuthVerifyRequest(BaseModel):
    user_id: str
    phone_code: str
    password: str | None = None


class TelegramUserSendRequest(BaseModel):
    user_id: str
    recipient_id: str
    text: str
