from pydantic import BaseModel

from ml.domain.models import ChatHistory, ModelMode, Tag, UserProfile


class MessagePayload(BaseModel):
    messages: ChatHistory  # converted via _wrap_messages
    chat_id: int
    tag: Tag
    mode: ModelMode
    file_url: str | None
    is_voice: bool
    profile: UserProfile
