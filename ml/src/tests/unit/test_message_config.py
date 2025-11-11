from ml.configs.message import ChatHistory, Message, Role


def test_chat_history_creates_distinct_message_lists() -> None:
    first_history = ChatHistory()
    second_history = ChatHistory()

    first_history.add_user("hello")

    assert first_history.messages == [Message(role=Role.user, content="hello")]
    assert second_history.messages == []


def test_add_system_returns_created_message() -> None:
    history = ChatHistory()

    msg = history.add_system("setup")

    assert msg == Message(role=Role.system, content="setup")
    assert history.messages == [msg]
