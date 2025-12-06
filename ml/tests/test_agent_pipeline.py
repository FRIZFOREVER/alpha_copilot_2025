from types import ModuleType, SimpleNamespace
from typing import Any, Callable
import sys

import pytest


class _ImportStateGraph:
    def __init__(self, *_: object, **__: object) -> None:
        return


langgraph_module = ModuleType("langgraph")
langgraph_graph_module = ModuleType("langgraph.graph")
langgraph_graph_module.END = "END"
langgraph_graph_module.StateGraph = _ImportStateGraph
sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", langgraph_graph_module)

router_module = ModuleType("ml.domain.workflow.router")
router_module.workflow = object()
router_module.workflow_collected = object()
sys.modules.setdefault("ml.domain.workflow.router", router_module)

ddgs_module = ModuleType("ddgs")


class _DummyDDGS:
    def __init__(self, *_: object, **__: object) -> None:
        return

    def text(self, *_: object, **__: object) -> list[str]:
        return []


ddgs_module.DDGS = _DummyDDGS
sys.modules.setdefault("ddgs", ddgs_module)

bs4_module = ModuleType("bs4")


class _DummyBeautifulSoup:
    def __init__(self, *_: object, **__: object) -> None:
        return

    def get_text(self, **__: object) -> str:
        return ""


bs4_module.BeautifulSoup = _DummyBeautifulSoup
sys.modules.setdefault("bs4", bs4_module)

external_module = ModuleType("ml.api.external")
external_module.__path__ = []  # type: ignore[attr-defined]
external_module.fetch_available_models = lambda *_: []
external_module.get_models_from_env = lambda *_: []
external_module.download_missing_models = lambda *_: None
external_module.clients_warmup = lambda *_: None
external_module.init_warmup_clients = lambda *_: None
external_module.read_minio_file = lambda *_: None
external_module.write_minio_file = lambda *_: None
external_module.GraphLogWebSocketClient = object
external_module.init_graph_log_client = lambda *_: None
external_module.send_graph_log = lambda *_: None
sys.modules.setdefault("ml.api.external", external_module)

ollama_client_module = ModuleType("ml.api.external.ollama_client")


class _DummyOllamaClient:
    def __init__(self, *_: object, **__: object) -> None:
        return


ollama_client_module.EmbeddingModelClient = _DummyOllamaClient
ollama_client_module.ReasoningModelClient = _DummyOllamaClient
sys.modules.setdefault("ml.api.external.ollama_client", ollama_client_module)

ollama_warmup_module = ModuleType("ml.api.external.ollama_warmup")
ollama_warmup_module.clients_warmup = external_module.clients_warmup
ollama_warmup_module.init_warmup_clients = external_module.init_warmup_clients
sys.modules.setdefault("ml.api.external.ollama_warmup", ollama_warmup_module)

ollama_init_module = ModuleType("ml.api.external.ollama_init")
ollama_init_module.download_missing_models = external_module.download_missing_models
ollama_init_module.fetch_available_models = external_module.fetch_available_models
ollama_init_module.get_models_from_env = external_module.get_models_from_env
sys.modules.setdefault("ml.api.external.ollama_init", ollama_init_module)

minio_client_module = ModuleType("ml.api.external.minio_client")
minio_client_module.read_minio_file = external_module.read_minio_file
minio_client_module.write_minio_file = external_module.write_minio_file
sys.modules.setdefault("ml.api.external.minio_client", minio_client_module)

websocket_client_module = ModuleType("ml.api.external.websocket_client")
websocket_client_module.GraphLogWebSocketClient = external_module.GraphLogWebSocketClient
websocket_client_module.init_graph_log_client = external_module.init_graph_log_client
websocket_client_module.send_graph_log = external_module.send_graph_log
sys.modules.setdefault("ml.api.external.websocket_client", websocket_client_module)


from ml.domain.workflow.agent import conditionals
from ml.domain.workflow.agent import pipeline


class _DummyStateGraph:
    def __init__(self, *_: object, **__: object) -> None:
        self.nodes: list[tuple[str, Callable[..., Any]]] = []
        self.edges: list[tuple[str, str]] = []
        self.conditional_edges: list[tuple[str, Callable[..., str], dict[str, str]]] = []
        self.entry_point: str | None = None
        self.compiled: bool = False

    def add_node(self, name: str, fn: Callable[..., Any]) -> None:
        self.nodes.append((name, fn))

    def add_edge(self, start: str, end: str) -> None:
        self.edges.append((start, end))

    def add_conditional_edges(
        self, start: str, decision_fn: Callable[..., str], mapping: dict[str, str]
    ) -> None:
        self.conditional_edges.append((start, decision_fn, mapping))

    def set_entry_point(self, name: str) -> None:
        self.entry_point = name

    def compile(self) -> "_DummyStateGraph":
        self.compiled = True
        return self


def test_create_pipeline_builds_expected_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    def _stub_node(_: object) -> str:
        return "stub"

    monkeypatch.setattr(pipeline, "StateGraph", _DummyStateGraph)
    monkeypatch.setattr(pipeline, "END", "END")

    monkeypatch.setattr(pipeline, "validate_voice", _stub_node)
    monkeypatch.setattr(pipeline, "validate_tag", _stub_node)
    monkeypatch.setattr(pipeline, "ingest_file", _stub_node)
    monkeypatch.setattr(pipeline, "define_mode", _stub_node)
    monkeypatch.setattr(pipeline, "final_stream", _stub_node)
    monkeypatch.setattr(pipeline, "flash_memories", _stub_node)
    monkeypatch.setattr(pipeline, "fast_answer", _stub_node)
    monkeypatch.setattr(pipeline, "thinking_planner", _stub_node)
    monkeypatch.setattr(pipeline, "research_tool_call", _stub_node)
    monkeypatch.setattr(pipeline, "research_observer", _stub_node)
    monkeypatch.setattr(pipeline, "research_reason", _stub_node)

    graph = pipeline.create_pipeline()

    assert isinstance(graph, _DummyStateGraph)
    assert graph.compiled is True
    assert graph.entry_point == "Voice validadtion"

    assert graph.nodes == [
        ("Voice validadtion", _stub_node),
        ("Tag validadtion", _stub_node),
        ("File ingestion", _stub_node),
        ("Mode definition", _stub_node),
        ("Final node", _stub_node),
        ("Flash memories", _stub_node),
        ("Fast answer", _stub_node),
        ("Thinking planner", _stub_node),
        ("Thinking tool call", _stub_node),
        ("Thinking observer", _stub_node),
        ("Research reason", _stub_node),
        ("Research tool call", _stub_node),
        ("Research observer", _stub_node),
    ]

    assert graph.edges == [
        ("Voice validadtion", "Tag validadtion"),
        ("Tag validadtion", "File ingestion"),
        ("File ingestion", "Mode definition"),
        ("Flash memories", "Fast answer"),
        ("Fast answer", "Final node"),
        ("Thinking planner", "Thinking tool call"),
        ("Thinking observer", "Thinking planner"),
        ("Research reason", "Research tool call"),
        ("Research observer", "Research reason"),
        ("Final node", "END"),
    ]

    assert graph.conditional_edges == [
        (
            "Mode definition",
            conditionals.mode_decision,
            {
                "fast_pipeline": "Flash memories",
                "thinking_pipeline": "Thinking planner",
                "research_pipeline": "Research reason",
            },
        ),
        (
            "Thinking tool call",
            conditionals.research_decision,
            {"tool_call": "Thinking observer", "finalize": "Final node"},
        ),
        (
            "Research tool call",
            conditionals.research_decision,
            {"tool_call": "Research observer", "finalize": "Final node"},
        ),
    ]


def test_mode_decision_errors_on_unknown_mode() -> None:
    state = SimpleNamespace(model_mode="unknown")

    with pytest.raises(RuntimeError, match="Failed to branch into pipeline"):
        conditionals.mode_decision(state)


def test_research_decision_uses_tool_information() -> None:
    final_tool_state = SimpleNamespace(last_executed_tool="final_answer", pending_tool_call=None)
    loop_tool_state = SimpleNamespace(last_executed_tool="other", pending_tool_call=None)

    assert conditionals.research_decision(final_tool_state) == "finalize"
    assert conditionals.research_decision(loop_tool_state) == "tool_call"


def test_research_decision_requires_tool_context() -> None:
    empty_state = SimpleNamespace(last_executed_tool=None, pending_tool_call=None)

    with pytest.raises(RuntimeError, match="No tool execution data available"):
        conditionals.research_decision(empty_state)
