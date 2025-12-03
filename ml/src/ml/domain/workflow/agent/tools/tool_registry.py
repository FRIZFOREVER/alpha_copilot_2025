from ml.domain.workflow.agent.tools import BaseTool
from ml.domain.workflow.agent.tools.final_answer.tool import FinalAnswerTool
from ml.domain.workflow.agent.tools.websearch.tool import WebSearchTool

_tool_registry: dict[str, BaseTool] = {}


def get_tool_registry() -> dict[str, BaseTool]:
    """Get the global tool registry."""
    return _tool_registry


def register_tool(tool: BaseTool) -> None:
    _tool_registry[tool.name] = tool


def get_tool(name: str) -> BaseTool | None:
    """Get a tool by name."""
    return _tool_registry.get(name)


def initialize_tools() -> None:
    """Initialize default tools."""
    register_tool(WebSearchTool())
    register_tool(FinalAnswerTool())


initialize_tools()
