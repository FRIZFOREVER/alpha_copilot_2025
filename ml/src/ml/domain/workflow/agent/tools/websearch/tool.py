from typing import Any

from ml.domain.workflow.agent.tools.base_tool import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    """Basic web search tool placeholder."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Searches the web and returns aggregated findings."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "query": {"type": "string", "description": "Поисковой запрос."},
            "required": ["query"],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        query_argument = kwargs.get("query")
        if query_argument is None:
            raise ValueError("web_search tool requires 'query' argument")

        # TODO: Implement
        return ToolResult(success=True, data={"query": query_argument, "results": []})
