from typing import Dict, Iterator, List
from unittest.mock import Mock, patch

from ml.agent.graph.pipeline import run_pipeline_stream
from ml.agent.graph.state import GraphState
from ml.configs.message import Message, Role


class DummyClient:
    def __init__(self) -> None:
        self.stream_calls: List[List[Dict[str, str]]] = []

    def stream(self, messages: List[Dict[str, str]]) -> Iterator[Dict[str, str]]:
        self.stream_calls.append(messages)
        return iter(())


def test_run_pipeline_stream_uses_graph_app_result() -> None:
    user_payload = {"role": "user", "content": "Hello"}
    final_state = GraphState(
        messages=[Message(role=Role.user, content="Hello")],
        final_prompt_messages=[{"role": "system", "content": "system"}],
    )

    fake_app = Mock()
    fake_app.invoke.return_value = final_state
    client = DummyClient()

    with patch("ml.agent.graph.pipeline._get_compiled_app", return_value=fake_app):
        chunks = list(run_pipeline_stream(client=client, messages=[user_payload]))

    assert chunks == []
    fake_app.invoke.assert_called_once()
    assert client.stream_calls == [final_state.final_prompt_messages]


def test_run_pipeline_stream_falls_back_to_stream_messages() -> None:
    user_payload = {"role": "user", "content": "Hello"}
    stream_messages = [{"role": "system", "content": "fallback"}]
    final_state = GraphState(
        messages=[Message(role=Role.user, content="Hello")],
        stream_messages=stream_messages,
    )

    fake_app = Mock()
    fake_app.invoke.return_value = final_state
    client = DummyClient()

    with patch("ml.agent.graph.pipeline._get_compiled_app", return_value=fake_app):
        list(run_pipeline_stream(client=client, messages=[user_payload]))

    assert client.stream_calls == [stream_messages]


def test_run_pipeline_stream_builds_prompt_when_missing() -> None:
    user_payload = {"role": "user", "content": "Hello"}
    final_state = GraphState(
        messages=[Message(role=Role.user, content="Hello")],
        mode="research",
        tool_results=[
            {
                "type": "search_result",
                "success": True,
                "data": {
                    "query": "Hello",
                    "results": [
                        {
                            "title": "Result 1",
                            "url": "http://example.com",
                            "snippet": "Snippet",
                        }
                    ],
                },
            }
        ],
    )

    fake_app = Mock()
    fake_app.invoke.return_value = final_state
    client = DummyClient()

    with patch("ml.agent.graph.pipeline._get_compiled_app", return_value=fake_app):
        list(run_pipeline_stream(client=client, messages=[user_payload]))

    assert len(client.stream_calls) == 1
    built_messages = client.stream_calls[0]
    assert built_messages[0]["role"] == "system"
    assert "Результаты поиска" in built_messages[1]["content"]
