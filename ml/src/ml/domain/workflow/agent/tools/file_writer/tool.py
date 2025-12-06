from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ml.api.external import write_minio_file
from ml.domain.models.tools_data import ToolResult
from ml.domain.workflow.agent.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class FileWriterTool(BaseTool):
    """Tool for creating a new file in MinIO from provided text content."""

    @property
    def name(self) -> str:
        return "file_writer"

    @property
    def description(self) -> str:
        return "Создает новый файл в MinIO из переданного содержимого и имени файла."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "Полное имя файла с расширением (например, report.txt).",
                },
                "content": {
                    "type": "string",
                    "description": "Текстовое содержимое файла.",
                },
            },
            "required": ["file_name", "content"],
            "description": "Создает файл в MinIO с учетом расширения из имени файла.",
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        file_name = kwargs.get("file_name")
        content = kwargs.get("content")

        if not isinstance(file_name, str):
            raise TypeError("file_writer tool requires 'file_name' to be a string")
        if file_name == "":
            raise ValueError("file_writer tool requires a non-empty 'file_name'")

        if not isinstance(content, str):
            raise TypeError("file_writer tool requires 'content' to be a string")
        if content == "":
            raise ValueError("file_writer tool requires non-empty 'content'")

        extension = self._extract_extension(file_name)

        try:
            write_minio_file(content, extension=extension)
        except Exception:
            logger.exception("Failed to write file '%s' to MinIO", file_name)
            raise

        evidence_text = (
            "Источник: файл\n"
            "Ожидаемый источник: файл\n"
            f"Создан новый файл: {file_name}"
        )

        return ToolResult(success=True, data=evidence_text)

    def _extract_extension(self, file_name: str) -> str:
        extension = Path(file_name).suffix
        if extension == "":
            raise ValueError("file_writer tool requires 'file_name' with an extension")
        return extension
