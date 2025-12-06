import pytest
from pydantic import ValidationError

from ml.api.schemas.message_payload import MessagePayload, ModelMode, Tag, UserProfile
from ml.domain.models.chat_history import Message, Role


def build_user_profile() -> UserProfile:
    return UserProfile(
        id=1,
        login="login",
        username="username",
        user_info="user info",
        business_info="business info",
        additional_instructions="be concise",
    )


def test_message_payload_accepts_valid_schema() -> None:
    payload = MessagePayload(
        messages=[
            Message(role=Role.system, content="guide"),
            Message(role=Role.user, content="question"),
        ],
        chat_id=1,
        tag=Tag.Finance,
        mode=ModelMode.Fast,
        file_url="https://example.com/file.txt",
        is_voice=True,
        profile=build_user_profile(),
    )

    assert payload.tag is Tag.Finance
    assert payload.mode is ModelMode.Fast
    assert payload.messages[0].role is Role.system
    assert payload.profile.username == "username"


def test_message_payload_rejects_invalid_tag() -> None:
    with pytest.raises(ValidationError):
        MessagePayload(
            messages=[
                Message(role=Role.system, content="guide"),
                Message(role=Role.user, content="question"),
            ],
            chat_id=2,
            tag="unknown",  # type: ignore[arg-type]
            mode=ModelMode.Auto,
            file_url="https://example.com/another.txt",
            is_voice=False,
            profile=build_user_profile(),
        )


def test_message_payload_enforces_chat_history_rules() -> None:
    with pytest.raises(ValidationError):
        MessagePayload(
            messages=[
                Message(role=Role.user, content="first"),
                Message(role=Role.user, content="second"),
            ],
            chat_id=3,
            tag=Tag.General,
            mode=ModelMode.Research,
            file_url="https://example.com/rules.txt",
            is_voice=False,
            profile=build_user_profile(),
        )


def test_message_payload_requires_complete_user_profile() -> None:
    with pytest.raises(ValidationError):
        MessagePayload(
            messages=[
                Message(role=Role.system, content="guide"),
                Message(role=Role.user, content="question"),
            ],
            chat_id=4,
            tag=Tag.Law,
            mode=ModelMode.Thiking,
            file_url="https://example.com/incomplete.txt",
            is_voice=False,
            profile={
                "id": 2,
                "login": "user_login",
                "username": "user2",
                "user_info": "info",
                "business_info": "biz",
            },
        )
