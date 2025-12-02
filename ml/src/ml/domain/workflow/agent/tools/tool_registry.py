# Global tool registry
from ml.domain.workflow.agent.tools import BaseTool
from ml.domain.workflow.agent.tools.websearch import WebSearchTool

_tool_registry: dict[str, BaseTool] = {}


def get_tool_registry() -> dict[str, BaseTool]:
    """Get the global tool registry."""
    return _tool_registry


def register_tool(tool: BaseTool) -> None:
    """Register a tool in the global registry."""
    _tool_registry[tool.name] = tool


def get_tool(name: str) -> BaseTool | None:
    """Get a tool by name."""
    return _tool_registry.get(name)


def initialize_tools() -> None:
    """Initialize default tools."""
    # Register web search tool
    register_tool(WebSearchTool())
    # Add more tools here as needed


# Initialize tools on import
initialize_tools()
