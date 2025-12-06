from __future__ import annotations

import io
import logging
import mimetypes
import time
import uuid
from pathlib import Path
from typing import ClassVar
from urllib.parse import urlparse

from fpdf import FPDF
from minio import Minio

logger = logging.getLogger(__name__)

DEFAULT_MINIO_ENDPOINT = "http://minio:9000"
DEFAULT_MINIO_ACCESS_KEY = "minio-user"
DEFAULT_MINIO_SECRET_KEY = "minio-password"
DEFAULT_BUCKET_NAME = "files"
UNICODE_FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
UNICODE_FONT_NAME = "DejaVuSans"


class MinioStorageClient:
    _instance: ClassVar[MinioStorageClient | None] = None

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket_name: str = DEFAULT_BUCKET_NAME,
    ) -> None:
        if getattr(self, "_initialized", False):
            return

        if not isinstance(bucket_name, str):
            raise TypeError("Bucket name must be a string")
        if bucket_name == "":
            raise ValueError("Bucket name must not be empty")

        parsed_endpoint = urlparse(endpoint or DEFAULT_MINIO_ENDPOINT)
        endpoint_host = parsed_endpoint.netloc or parsed_endpoint.path
        if endpoint_host == "":
            raise ValueError("MinIO endpoint is not provided")

        self.bucket_name = bucket_name
        self._client = Minio(
            endpoint_host,
            access_key=access_key or DEFAULT_MINIO_ACCESS_KEY,
            secret_key=secret_key or DEFAULT_MINIO_SECRET_KEY,
            secure=parsed_endpoint.scheme == "https",
        )

        if not self._client.bucket_exists(self.bucket_name):
            msg = f"MinIO bucket '{self.bucket_name}' is not available"
            logger.error(msg)
            raise RuntimeError(msg)

        self._initialized = True

    @classmethod
    def instance(cls) -> MinioStorageClient:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _normalize_object_path(self, object_path: str) -> str:
        if not isinstance(object_path, str):
            raise TypeError("Object path must be a string")
        if object_path == "":
            raise ValueError("Object path must not be empty")

        normalized_path = object_path
        if normalized_path.startswith("/"):
            normalized_path = normalized_path[1:]

        bucket_prefix = f"{self.bucket_name}/"
        if normalized_path.startswith(bucket_prefix):
            return normalized_path[len(bucket_prefix) :]

        return normalized_path

    def _normalize_extension(self, extension: str) -> str:
        if not isinstance(extension, str):
            raise TypeError("File extension must be a string")
        if extension == "":
            raise ValueError("File extension must not be empty")

        if extension.startswith("."):
            return extension

        return f".{extension}"

    def _guess_content_type(self, extension: str) -> str:
        guessed_type = mimetypes.types_map.get(extension.lower())
        if isinstance(guessed_type, str):
            return guessed_type
        return "application/octet-stream"

    def _build_object_name(self, extension: str) -> str:
        timestamp = int(time.time())
        return f"{uuid.uuid4()}_{timestamp}{extension}"

    def _render_pdf(self, content: str) -> bytes:
        if not isinstance(content, str):
            raise TypeError("PDF content must be a string")

        if not UNICODE_FONT_PATH.is_file():
            raise FileNotFoundError(f"Unicode font file not found at {UNICODE_FONT_PATH}")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_compression(False)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font(UNICODE_FONT_NAME, fname=str(UNICODE_FONT_PATH), uni=True)
        pdf.set_font(UNICODE_FONT_NAME, size=12)
        pdf.multi_cell(0, 10, text=content)
        rendered = pdf.output()

        if not isinstance(rendered, (bytes, bytearray)):
            raise TypeError("PDF renderer returned unexpected data type")

        return bytes(rendered)

    def read_text(self, object_path: str) -> str:
        object_name = self._normalize_object_path(object_path)
        try:
            response = self._client.get_object(self.bucket_name, object_name)
        except Exception:
            logger.exception(
                "Failed to fetch object %s from bucket %s", object_name, self.bucket_name
            )
            raise

        try:
            data = response.read()
        finally:
            response.close()
            response.release_conn()

        try:
            return data.decode("utf-8")
        except Exception:
            logger.exception(
                "Failed to decode object %s from bucket %s as UTF-8 text",
                object_name,
                self.bucket_name,
            )
            raise

    def write_text(self, content: str, *, extension: str = "txt") -> str:
        if not isinstance(content, str):
            raise TypeError("File content must be a string")

        normalized_extension = self._normalize_extension(extension)
        object_name = self._build_object_name(normalized_extension)
        content_type = self._guess_content_type(normalized_extension)
        encoded_content = (
            self._render_pdf(content)
            if normalized_extension.lower() == ".pdf"
            else content.encode("utf-8")
        )

        try:
            self._client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(encoded_content),
                length=len(encoded_content),
                content_type=content_type,
            )
        except Exception:
            logger.exception(
                "Failed to upload object %s to bucket %s", object_name, self.bucket_name
            )
            raise

        return f"/{self.bucket_name}/{object_name}"


def read_minio_file(object_path: str) -> str:
    client = MinioStorageClient.instance()
    return client.read_text(object_path)


def write_minio_file(content: str, *, extension: str = "txt") -> str:
    client = MinioStorageClient.instance()
    return client.write_text(content, extension=extension)
