from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from ml.api.external import read_minio_file
from ml.domain.models.tools_data import ToolResult
from ml.domain.workflow.agent.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class FileReaderTool(BaseTool):
    """Tool for fetching a file from MinIO using a pre-provided URL."""

    @property
    def name(self) -> str:
        return "file_reader"

    @property
    def description(self) -> str:
        return "Загружает содержимое файла из MinIO по переданному file_url."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "description": "Использует file_url из запроса автоматически. Аргументы не требуются.",
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        file_url = kwargs.get("file_url")
        if file_url is None:
            raise ValueError("file_reader tool requires 'file_url' argument")
        if not isinstance(file_url, str):
            raise TypeError("file_reader tool requires 'file_url' to be a string")
        if file_url == "":
            raise ValueError("file_reader tool received an empty file_url")

        object_path = self._extract_object_path(file_url)

        try:
            file_contents = read_minio_file(object_path)
        except Exception:
            logger.exception("Failed to read file from MinIO at %s", object_path)
            raise

        evidence_text = (
            "Источник: файл\n"
            f"Путь к файлу: {file_url}\n"
            f"Содержимое файла:\n{file_contents}"
        )

        return ToolResult(success=True, data=evidence_text)

    def _extract_object_path(self, file_url: str) -> str:
        parsed_url = urlparse(file_url)
        if parsed_url.path:
            return parsed_url.path

        if parsed_url.scheme or parsed_url.netloc:
            raise ValueError("file_reader tool could not resolve object path from file_url")

        return file_url
