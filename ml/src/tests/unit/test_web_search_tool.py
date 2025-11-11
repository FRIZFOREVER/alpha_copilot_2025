import pytest

from ml.agent.tools import page_text
from ml.agent.tools.web_search import WebSearchTool


class _DummyDDGS:
    def __init__(self, results):
        self._results = results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def text(self, query, max_results):  # pragma: no cover - interface compatibility
        return list(self._results)


def _patch_ddgs(monkeypatch, results):
    monkeypatch.setattr(
        "ml.agent.tools.web_search.DDGS",
        lambda: _DummyDDGS(results),
    )


def test_execute_enriches_results_with_page_content(monkeypatch):
    dummy_results = [
        {
            "title": "Example Title",
            "href": "https://example.com/article",
            "body": "Original snippet",
        }
    ]
    _patch_ddgs(monkeypatch, dummy_results)

    sample_html = """
        <html>
            <body>
                <h1>Example Title</h1>
                <p>This demo page mentions the Query term to build an excerpt.</p>
            </body>
        </html>
    """

    monkeypatch.setattr(
        page_text,
        "fetch_page_html",
        lambda url, timeout, max_bytes: sample_html,
    )

    tool = WebSearchTool(max_results=1)
    result = tool.execute("Query")

    assert result.success
    assert result.data["count"] == 1

    enriched = result.data["results"][0]
    assert enriched["url"] == "https://example.com/article"
    assert enriched["snippet"] == "Original snippet"
    assert "query" in enriched["excerpt"].lower()
    assert enriched["excerpt"] != enriched["snippet"]
    assert "Example Title" in enriched["content"]


def test_execute_falls_back_to_snippet_on_fetch_failure(monkeypatch):
    dummy_results = [
        {
            "title": "Broken result",
            "href": "https://example.com/broken",
            "body": "Original snippet",
        }
    ]
    _patch_ddgs(monkeypatch, dummy_results)

    def raising_fetch(*_, **__):
        raise RuntimeError("network down")

    def fail_html_to_text(*_, **__):  # pragma: no cover - ensure not called
        raise AssertionError("html_to_text should not be invoked")

    def fail_build_excerpt(*_, **__):  # pragma: no cover - ensure not called
        raise AssertionError("build_excerpt should not be invoked")

    monkeypatch.setattr(page_text, "fetch_page_html", raising_fetch)
    monkeypatch.setattr(page_text, "html_to_text", fail_html_to_text)
    monkeypatch.setattr(page_text, "build_excerpt", fail_build_excerpt)

    tool = WebSearchTool(max_results=1)
    result = tool.execute("Query")

    assert result.success
    enriched = result.data["results"][0]
    assert enriched["excerpt"] == enriched["snippet"] == "Original snippet"
    assert "content" not in enriched


def test_html_to_text_strips_non_content_elements():
    html = """
        <html>
            <head>
                <style>body {color: red;}</style>
                <script>console.log('ignore');</script>
            </head>
            <body>
                <h1>Headline</h1>
                <p>Paragraph with    irregular\n whitespace.</p>
            </body>
        </html>
    """

    text = page_text.html_to_text(html)

    assert "console.log" not in text
    assert "style" not in text.lower()
    assert text == "Headline Paragraph with irregular whitespace."


@pytest.mark.parametrize(
    "text, query, window, expected",
    [
        ("Alpha beta gamma delta", "gamma", 5, "...gamma delta"),
        ("Alpha beta gamma delta", "zeta", 5, "Alpha beta"),
        ("  Extra   spaces text  ", "extra", 0, "Extra spaces text"),
    ],
)
def test_build_excerpt_behaviour(text, query, window, expected):
    excerpt = page_text.build_excerpt(text, query, window=window)
    assert excerpt.startswith(expected)
