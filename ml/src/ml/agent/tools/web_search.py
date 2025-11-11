from typing import Any, Dict
from duckduckgo_search import DDGS
from ml.agent.tools.base import BaseTool, ToolResult
import logging

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """DuckDuckGo web search tool."""
    
    def __init__(self, max_results: int = 5):
        self._max_results = max_results
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Поиск информации в интернете с помощью DuckDuckGo. Возвращает результаты поиска с заголовками, ссылками и краткими описаниями."
    
    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    
    def execute(self, query: str, **kwargs: Any) -> ToolResult:
        """
        Execute web search.
        
        Args:
            query: Search query string
            
        Returns:
            ToolResult with search results
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self._max_results))
            
            # Format results
            formatted_results = [
                {
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                }
                for result in results
            ]
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": formatted_results,
                    "count": len(formatted_results)
                }
            )
        except Exception as e:
            logger.error(f"Web search error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )

