from typing import List
from unittest.mock import Mock

from ml.agent.graph.nodes.evidence import EvidenceSummary, extract_evidence_node
from ml.agent.graph.state import GraphState


def _make_search_state(facts_payload: List[dict]) -> GraphState:
    return GraphState(
        tool_results=[
            {
                "type": "search_result",
                "success": True,
                "data": {
                    "query": "test query",
                    "results": facts_payload,
                },
            }
        ]
    )


def test_extract_evidence_node_uses_structured_summary() -> None:
    state = _make_search_state(
        [
            {
                "title": "Example title",
                "url": "http://example.com",
                "content": "Example content with multiple details.",
            }
        ]
    )

    summary = EvidenceSummary(
        title="Example title",
        url="http://example.com",
        facts=["Первый факт", "Второй факт"],
    )

    client = Mock()
    client.call_structured.return_value = summary

    updated = extract_evidence_node(state, client)

    assert updated.evidence == [
        {
            "title": "Example title",
            "url": "http://example.com",
            "facts": ["Первый факт", "Второй факт"],
            "query": "test query",
            "fallback": False,
        }
    ]
    client.call_structured.assert_called_once()
