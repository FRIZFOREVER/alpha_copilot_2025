import pytest

from ml.domain.models.chat_history import ChatHistory, Message, Role


def test_validate_turn_order_accepts_alternating() -> None:
    history = ChatHistory(
        messages=[
            Message(role=Role.system, content="system message"),
            Message(role=Role.user, content="hello"),
            Message(role=Role.assistant, content="hi"),
            Message(role=Role.user, content="follow up"),
        ]
    )

    assert len(history.messages) == 4


def test_validate_turn_order_rejects_consecutive_non_system() -> None:
    with pytest.raises(ValueError):
        ChatHistory(
            messages=[
                Message(role=Role.user, content="first"),
                Message(role=Role.user, content="second"),
            ]
        )


def test_validate_turn_order_rejects_consecutive_assistant_messages() -> None:
    with pytest.raises(ValueError):
        ChatHistory(
            messages=[
                Message(role=Role.assistant, content="first reply"),
                Message(role=Role.assistant, content="second reply"),
            ]
        )


def test_add_user_rejects_consecutive_user_messages() -> None:
    history = ChatHistory(messages=[Message(role=Role.user, content="first")])

    with pytest.raises(RuntimeError):
        history.add_user("second")


def test_add_assistant_rejects_consecutive_assistant_messages() -> None:
    history = ChatHistory(messages=[Message(role=Role.assistant, content="first reply")])

    with pytest.raises(RuntimeError):
        history.add_assistant("another reply")


def test_add_user_and_assistant_append_in_turn_order() -> None:
    history = ChatHistory(messages=[Message(role=Role.system, content="initial")])

    history.add_user("hello")
    history.add_assistant("hi there")

    assert history.messages[-2].role is Role.user
    assert history.messages[-2].content == "hello"
    assert history.messages[-1].role is Role.assistant
    assert history.messages[-1].content == "hi there"


def test_add_or_change_system_replaces_previous_system_message() -> None:
    history = ChatHistory(
        messages=[
            Message(role=Role.system, content="initial"),
            Message(role=Role.user, content="hello"),
            Message(role=Role.assistant, content="reply"),
        ]
    )

    history.add_or_change_system("replacement")

    assert history.messages[0].role is Role.system
    assert history.messages[0].content == "replacement"
    assert len([message for message in history.messages if message.role is Role.system]) == 1


def test_last_message_raises_on_empty_history() -> None:
    history = ChatHistory(messages=[])

    with pytest.raises(RuntimeError):
        history.last_message()


def test_last_message_requires_user_message_when_ensure_flag_set() -> None:
    history = ChatHistory(messages=[Message(role=Role.assistant, content="reply")])

    with pytest.raises(ValueError):
        history.last_message(ensure_user=True)


def test_model_dump_chat_last_returns_latest_user_message() -> None:
    history = ChatHistory(
        messages=[
            Message(role=Role.system, content="guide"),
            Message(role=Role.user, content="question"),
            Message(role=Role.assistant, content="answer"),
            Message(role=Role.user, content="follow up"),
        ]
    )

    assert history.model_dump_chat_last() == [
        {"role": Role.user, "content": "follow up"},
    ]


def test_model_dump_chat_last_raises_on_empty_history() -> None:
    history = ChatHistory(messages=[])

    with pytest.raises(RuntimeError):
        history.model_dump_chat_last()


def test_model_dump_chat_returns_expected_shape() -> None:
    history = ChatHistory(
        messages=[
            Message(role=Role.system, content="guide"),
            Message(role=Role.user, content="question"),
        ]
    )

    dumped = history.model_dump_chat()

    assert dumped == [
        {"role": "system", "content": "guide"},
        {"role": "user", "content": "question"},
    ]


def test_message_rejects_system_id() -> None:
    with pytest.raises(ValueError) as exc_info:
        Message(role=Role.system, content="guide", id=123)

    assert "System messages must not have an id (id must be None)." in str(exc_info.value)


def test_message_accepts_ids_for_non_system_roles() -> None:
    user_message = Message(role=Role.user, content="question", id=1)
    assistant_message = Message(role=Role.assistant, content="response", id=2)

    assert user_message.id == 1
    assert assistant_message.id == 2


def test_last_user_message_id_returns_latest_user_id() -> None:
    history = ChatHistory(
        messages=[
            Message(role=Role.user, content="first", id=3),
            Message(role=Role.assistant, content="reply"),
            Message(role=Role.user, content="second", id=7),
        ]
    )

    assert history.last_user_message_id() == 7


def test_last_user_message_id_requires_id_presence() -> None:
    history = ChatHistory(messages=[Message(role=Role.user, content="question")])

    with pytest.raises(ValueError):
        history.last_user_message_id()


def test_last_user_message_id_requires_last_message_is_user() -> None:
    history = ChatHistory(messages=[Message(role=Role.assistant, content="reply", id=5)])

    with pytest.raises(ValueError):
        history.last_user_message_id()
