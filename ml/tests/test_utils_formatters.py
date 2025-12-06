import pytest
from ollama import ProgressResponse

from ml.domain.models.payload_data import UserProfile
from ml.domain.models.tools_data import Evidence, ToolResult
from ml.utils.download_formatters import format_bytes, format_progress
from ml.utils.pipeline_data_formatters import (
    _format_evidence,
    _format_created_file_evidence,
    _format_file_evidence,
    _format_web_evidence,
    format_research_observations,
    get_system_prompt,
)


@pytest.mark.parametrize(
    "value, expected",
    [(None, "unknown"), (512, "512.0B"), (1536, "  1.5KB"), (5_242_880, "  5.0MB")],
)
def test_format_bytes(value: int | None, expected: str) -> None:
    assert format_bytes(value) == expected


def test_format_progress_with_known_total() -> None:
    progress = ProgressResponse(
        model="test",
        status="downloading",
        completed=512,
        total=1024,
        digest="digest",
        context=None,
    )

    assert (
        format_progress(progress)
        == "downloading [██████████----------]  50.0% 512.0B/  1.0KB"
    )


def test_format_progress_without_total() -> None:
    progress = ProgressResponse(
        model="test",
        status=None,
        completed=300,
        total=None,
        digest="digest",
        context=None,
    )

    assert format_progress(progress) == "pulling 300.0B"


def test_format_file_evidence_outputs_content() -> None:
    tool_result = ToolResult(success=True, data="File contents", error=None)

    assert _format_file_evidence(1, tool_result) == (
        "1. Источник: загруженный файл (tool: file_reader)\nFile contents"
    )


def test_format_file_evidence_rejects_non_string_data() -> None:
    tool_result = ToolResult(success=True, data=123, error=None)

    with pytest.raises(TypeError):
        _format_file_evidence(1, tool_result)


def test_format_created_file_evidence_outputs_message_and_url() -> None:
    tool_result = ToolResult(
        success=True,
        data={"message": "Created file report.txt", "file_url": "http://example.com"},
        error=None,
    )

    assert _format_created_file_evidence(1, tool_result) == (
        "1. Источник: созданный файл (tool: file_writer)\n"
        "Created file report.txt\n"
        "URL файла: http://example.com"
    )


def test_format_created_file_evidence_validates_input() -> None:
    invalid_type_result = ToolResult(success=True, data="not a dict", error=None)
    missing_message_result = ToolResult(success=True, data={"file_url": "url"}, error=None)
    missing_file_url_result = ToolResult(success=True, data={"message": "msg"}, error=None)
    wrong_types_result = ToolResult(
        success=True,
        data={"message": 123, "file_url": 456},
        error=None,
    )

    with pytest.raises(TypeError):
        _format_created_file_evidence(1, invalid_type_result)

    with pytest.raises(ValueError):
        _format_created_file_evidence(1, missing_message_result)

    with pytest.raises(ValueError):
        _format_created_file_evidence(1, missing_file_url_result)

    with pytest.raises(TypeError):
        _format_created_file_evidence(1, wrong_types_result)


def test_format_web_evidence_outputs_results() -> None:
    tool_result = ToolResult(
        success=True,
        data={
            "query": "alpha",
            "results": [
                {
                    "url": "https://example.com",
                    "title": "Example",
                    "content": "Example content",
                }
            ],
        },
        error=None,
    )

    assert _format_web_evidence(2, tool_result) == (
        "2. Источник: веб-поиск (tool: web_search)\n"
        "Поисковый запрос: alpha\n"
        "Детали результатов:\n"
        "- Результат 1: Example\n  URL: https://example.com\n  Извлечённый текст:\n"
        "Example content"
    )


def test_format_web_evidence_requires_dictionary() -> None:
    tool_result = ToolResult(success=True, data="text", error=None)

    with pytest.raises(TypeError):
        _format_web_evidence(1, tool_result)


def test_format_web_evidence_requires_query_and_results() -> None:
    tool_result_missing_query = ToolResult(success=True, data={"results": []}, error=None)
    tool_result_missing_results = ToolResult(success=True, data={"query": "x"}, error=None)

    with pytest.raises(ValueError):
        _format_web_evidence(1, tool_result_missing_query)

    with pytest.raises(ValueError):
        _format_web_evidence(1, tool_result_missing_results)


def test_format_web_evidence_validates_result_entries() -> None:
    tool_result_wrong_list = ToolResult(
        success=True,
        data={"query": "alpha", "results": "not a list"},
        error=None,
    )
    tool_result_missing_fields = ToolResult(
        success=True,
        data={"query": "alpha", "results": [{}]},
        error=None,
    )
    tool_result_wrong_types = ToolResult(
        success=True,
        data={
            "query": "alpha",
            "results": [
                {"url": 10, "title": "t", "content": "c"},
            ],
        },
        error=None,
    )

    with pytest.raises(TypeError):
        _format_web_evidence(1, tool_result_wrong_list)

    with pytest.raises(ValueError):
        _format_web_evidence(1, tool_result_missing_fields)

    with pytest.raises(TypeError):
        _format_web_evidence(1, tool_result_wrong_types)


def test_format_evidence_delegates_to_specific_handlers() -> None:
    file_result = ToolResult(success=True, data="content", error=None)
    web_result = ToolResult(
        success=True,
        data={"query": "alpha", "results": [{"url": "u", "title": "t", "content": "c"}]},
        error=None,
    )
    file_writer_result = ToolResult(
        success=True,
        data={"message": "Created report.txt", "file_url": "http://example.com"},
        error=None,
    )
    default_result = ToolResult(success=True, data="unused", error=None)

    file_evidence = Evidence(tool_name="file_reader", summary="", source=file_result)
    web_evidence = Evidence(tool_name="web_search", summary="", source=web_result)
    file_writer_evidence = Evidence(
        tool_name="file_writer", summary="", source=file_writer_result
    )
    other_evidence = Evidence(tool_name="custom", summary="summary", source=default_result)

    assert _format_evidence(1, file_evidence) == (
        "1. Источник: загруженный файл (tool: file_reader)\ncontent"
    )
    assert _format_evidence(2, web_evidence).startswith(
        "2. Источник: веб-поиск (tool: web_search)\nПоисковый запрос: alpha"
    )
    assert _format_evidence(3, file_writer_evidence).startswith(
        "3. Источник: созданный файл (tool: file_writer)"
    )
    assert _format_evidence(4, other_evidence) == (
        "4. Источник: инструмент custom\nДанные:\nsummary"
    )


def test_format_research_observations_combines_entries() -> None:
    evidence = [
        Evidence(
            tool_name="file_reader",
            summary="file summary",
            source=ToolResult(success=True, data="data1", error=None),
        ),
        Evidence(
            tool_name="web_search",
            summary="web summary",
            source=ToolResult(
                success=True,
                data={
                    "query": "alpha",
                    "results": [
                        {
                            "url": "https://example.com",
                            "title": "Example",
                            "content": "Example content",
                        }
                    ],
                },
                error=None,
            ),
        ),
    ]

    formatted = format_research_observations(evidence)

    assert "1. Источник: загруженный файл" in formatted
    assert "2. Источник: веб-поиск" in formatted


def test_get_system_prompt_includes_user_data_and_evidence() -> None:
    profile = UserProfile(
        id=1,
        login="user",
        username="Имя Отчество",
        user_info="description",
        business_info="business",
        additional_instructions="follow rules",
    )
    evidence = [
        Evidence(
            tool_name="file_reader",
            summary="summary",
            source=ToolResult(success=True, data="file text", error=None),
        )
    ]

    prompt = get_system_prompt(profile, evidence)

    assert "Имя Отчество" in prompt
    assert "file text" in prompt
    assert "дополнительных инструкций" not in prompt
