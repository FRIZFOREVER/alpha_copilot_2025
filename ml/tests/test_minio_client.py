import io
import uuid
from typing import Any, Dict

import pytest

from ml.api.external import minio_client


class FakeResponse:
    def __init__(self, *, payload: bytes) -> None:
        self._payload = payload
        self.closed = False
        self.released = False

    def read(self, amt: int | None = None) -> bytes:  # noqa: ARG002 - amt not used
        return self._payload

    def close(self) -> None:
        self.closed = True

    def release_conn(self) -> None:
        self.released = True


class FakeMinio:
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
        self.args = args
        self.kwargs = kwargs
        self.put_calls: list[Dict[str, Any]] = []
        self._objects: Dict[str, FakeResponse] = {}

    def bucket_exists(self, bucket_name: str) -> bool:  # noqa: D401
        return True

    def get_object(self, bucket_name: str, object_name: str) -> FakeResponse:
        key = f"{bucket_name}/{object_name}"
        response = self._objects.get(key)
        if response is None:
            raise FileNotFoundError(key)
        return response

    def put_object(
        self,
        bucket_name: str,
        object_name: str,
        data: io.BytesIO,
        *,
        length: int,
        content_type: str,
    ) -> None:
        self.put_calls.append(
            {
                "bucket": bucket_name,
                "object_name": object_name,
                "length": length,
                "content_type": content_type,
            }
        )
        payload = data.getvalue()
        self._objects[f"{bucket_name}/{object_name}"] = FakeResponse(payload=payload)


@pytest.fixture(autouse=True)
def reset_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(minio_client.MinioStorageClient, "_instance", None)
    monkeypatch.setattr(minio_client, "Minio", FakeMinio)


@pytest.fixture()
def fixed_uuid(monkeypatch: pytest.MonkeyPatch) -> uuid.UUID:
    value = uuid.UUID("12345678-1234-5678-1234-567812345678")
    monkeypatch.setattr(minio_client.uuid, "uuid4", lambda: value)
    return value


@pytest.fixture()
def fixed_timestamp(monkeypatch: pytest.MonkeyPatch) -> int:
    timestamp = 1_700_000_000
    monkeypatch.setattr(minio_client.time, "time", lambda: timestamp)
    return timestamp


def test_write_text_uploads_and_returns_path(
    monkeypatch: pytest.MonkeyPatch, fixed_uuid: uuid.UUID, fixed_timestamp: int
) -> None:
    fake = FakeMinio()
    monkeypatch.setattr(minio_client, "Minio", lambda *args, **kwargs: fake)

    path = minio_client.write_minio_file("hello", extension=".txt")

    expected_name = f"{fixed_uuid}_{fixed_timestamp}.txt"
    assert path == f"/files/{expected_name}"
    assert fake.put_calls == [
        {
            "bucket": "files",
            "object_name": expected_name,
            "length": 5,
            "content_type": "text/plain",
        }
    ]


def test_write_pdf_generates_valid_document(
    monkeypatch: pytest.MonkeyPatch, fixed_uuid: uuid.UUID, fixed_timestamp: int
) -> None:
    fake = FakeMinio()
    monkeypatch.setattr(minio_client, "Minio", lambda *args, **kwargs: fake)

    path = minio_client.write_minio_file("pdf content", extension=".pdf")

    expected_name = f"{fixed_uuid}_{fixed_timestamp}.pdf"
    assert path == f"/files/{expected_name}"
    assert fake.put_calls == [
        {
            "bucket": "files",
            "object_name": expected_name,
            "length": len(fake._objects[f"files/{expected_name}"].read()),
            "content_type": "application/pdf",
        }
    ]
    payload = fake._objects[f"files/{expected_name}"].read()
    assert payload.startswith(b"%PDF")
    assert b"pdf content" in payload


def test_read_text_fetches_object(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeMinio()
    fake._objects["files/sample.txt"] = FakeResponse(payload=b"sample text")
    monkeypatch.setattr(minio_client, "Minio", lambda *args, **kwargs: fake)

    content = minio_client.read_minio_file("/files/sample.txt")

    assert content == "sample text"


def test_read_text_uses_bucket_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeMinio()
    fake._objects["files/prefix/inner.txt"] = FakeResponse(payload=b"ok")
    monkeypatch.setattr(minio_client, "Minio", lambda *args, **kwargs: fake)

    content = minio_client.read_minio_file("files/prefix/inner.txt")

    assert content == "ok"


@pytest.mark.parametrize("extension, expected", [("txt", ".txt"), (".md", ".md")])
def test_normalize_extension(monkeypatch: pytest.MonkeyPatch, extension: str, expected: str) -> None:
    fake = FakeMinio()
    monkeypatch.setattr(minio_client, "Minio", lambda *args, **kwargs: fake)
    client = minio_client.MinioStorageClient.instance()

    assert client._normalize_extension(extension) == expected


@pytest.mark.parametrize(
    "path, normalized",
    [
        ("/files/name.txt", "name.txt"),
        ("files/name.txt", "name.txt"),
        ("/files/nested/name.txt", "nested/name.txt"),
    ],
)
def test_normalize_object_path(monkeypatch: pytest.MonkeyPatch, path: str, normalized: str) -> None:
    fake = FakeMinio()
    monkeypatch.setattr(minio_client, "Minio", lambda *args, **kwargs: fake)
    client = minio_client.MinioStorageClient.instance()

    assert client._normalize_object_path(path) == normalized
