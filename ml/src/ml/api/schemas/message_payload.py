from enum import Enum

from pydantic import BaseModel

from ml.domain.models import ChatHistory


class UserProfile(BaseModel):
    id: int
    login: str
    username: str
    user_info: str
    business_info: str
    additional_instructions: str


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
    Empty = ""


class MessagePayload(ChatHistory):
    chat_id: int
    tag: Tag
    mode: ModelMode
    file_url: str
    is_voice: bool
    profile: UserProfile
