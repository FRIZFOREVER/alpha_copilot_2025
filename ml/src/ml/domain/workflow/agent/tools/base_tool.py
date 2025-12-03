from abc import ABC, abstractmethod
from typing import Any

from ml.domain.models.tools_data import ToolResult


class BaseTool(ABC):
    """Base class for all tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def schema(self) -> dict[str, Any]:
        """JSON schema for tool arguments."""
        pass

    def tool_description(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "schema": self.schema}

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute the tool with given arguments.

        Args:
            **kwargs: Tool arguments

        Returns:
            ToolResult with execution result
        """
        pass
