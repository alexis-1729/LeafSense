from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import documents
from app.core.security import require_admin
from app.infrastructure.document_extractor import DocumentExtractor
from app.infrastructure.persistence.document_repo import DocumentRepository


@pytest.fixture
def ingest_client(monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, dict]:
    created: dict = {}
    document_id = uuid4()
    timestamp = datetime.now(UTC)

    class FakeRepository:
        def __init__(self, _connection: object) -> None:
            self.connection = _connection

        def create(self, **values: object) -> dict[str, object]:
            created.update(values)
            return {"id": document_id, "status": "pending"}

        def get_status(self, _document_id: UUID) -> dict[str, object]:
            return {
                "id": _document_id,
                "pest_label": "roya",
                "crop": "café",
                "source": "guía",
                "language": "es",
                "filename": "document.txt",
                "status": "indexed",
                "chunk_count": 2,
                "error": None,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

    app = FastAPI()
    app.state.settings = SimpleNamespace(max_document_bytes=64)
    app.state.document_extractor = DocumentExtractor()
    app.dependency_overrides[require_admin] = lambda: {"role": "admin"}
    app.dependency_overrides[documents.get_connection] = lambda: object()
    app.include_router(documents.router)
    monkeypatch.setattr(documents, "DocumentRepository", FakeRepository)
    return TestClient(app), created


def test_extract_plain_text_and_markdown() -> None:
    assert DocumentExtractor.extract(b"\xef\xbb\xbfTexto de prueba", "txt") == "Texto de prueba"
    assert DocumentExtractor.extract(b"# Guia", "md") == "# Guia"


def test_extract_rejects_invalid_utf8() -> None:
    with pytest.raises(ValueError, match="could not be parsed"):
        DocumentExtractor.extract(b"\xff", "txt")


def test_extract_rejects_unsupported_extension() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        DocumentExtractor.extract(b"data", "docx")


def test_document_status_query_includes_chunk_count() -> None:
    class FakeCursor:
        query = ""
        parameters: tuple[object, ...] = ()

        def __enter__(self) -> "FakeCursor":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def execute(self, query: str, _parameters: tuple[object, ...]) -> None:
            self.query = query
            self.parameters = _parameters

        def fetchone(self) -> dict[str, object]:
            now = datetime.now(UTC)
            return {
                "id": uuid4(),
                "pest_label": "roya",
                "crop": "café",
                "source": "guía",
                "language": "es",
                "filename": "document.txt",
                "status": "indexed",
                "error": None,
                "chunk_count": 2,
                "created_at": now,
                "updated_at": now,
            }

    class FakeConnection:
        def __init__(self) -> None:
            self.fake_cursor = FakeCursor()

        def cursor(self, **_: object) -> FakeCursor:
            return self.fake_cursor

    connection = FakeConnection()
    document_id = uuid4()

    result = DocumentRepository(connection).get_status(document_id)

    assert result is not None
    assert result["chunk_count"] == 2
    assert "chunk_count" in connection.fake_cursor.query
    assert connection.fake_cursor.parameters == (document_id,)


def test_mark_indexed_reads_row_count_before_cursor_closes() -> None:
    class FakeCursor:
        closed = False

        @property
        def rowcount(self) -> int:
            return -1 if self.closed else 1

        def __enter__(self) -> "FakeCursor":
            return self

        def __exit__(self, *_: object) -> None:
            self.closed = True

        def execute(self, _query: str, _parameters: tuple[object, ...]) -> None:
            self.query = _query
            self.parameters = _parameters

    class FakeConnection:
        def cursor(self) -> FakeCursor:
            return FakeCursor()

    repository = DocumentRepository(FakeConnection())

    assert repository.mark_indexed(uuid4(), 2)


def test_document_status_response_includes_chunk_count(
    ingest_client: tuple[TestClient, dict],
) -> None:
    client, _ = ingest_client
    document_id = uuid4()

    response = client.get(f"/rag/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["chunk_count"] == 2


def test_ingest_document_accepts_text_input(ingest_client: tuple[TestClient, dict]) -> None:
    client, created = ingest_client

    response = client.post(
        "/rag/documents",
        data={
            "text": "Descripción de la plaga",
            "pest_label": "roya",
            "crop": "café",
            "source": "guía",
            "language": "ES",
        },
    )

    assert response.status_code == 202
    assert response.json()["status"] == "pending"
    assert created == {
        "text": "Descripción de la plaga",
        "pest_label": "roya",
        "crop": "café",
        "source": "guía",
        "language": "es",
        "filename": "document.txt",
    }


def test_ingest_document_accepts_file_input(
    ingest_client: tuple[TestClient, dict],
) -> None:
    client, created = ingest_client

    response = client.post(
        "/rag/documents",
        data={
            "pest_label": "roya",
            "crop": "café",
            "source": "guía",
            "language": "es",
        },
        files={"file": ("guide.md", b"# Manejo de roya", "text/markdown")},
    )

    assert response.status_code == 202
    assert created["text"] == "# Manejo de roya"
    assert created["filename"] == "guide.md"


def test_ingest_document_rejects_both_file_and_text(
    ingest_client: tuple[TestClient, dict],
) -> None:
    client, _ = ingest_client

    response = client.post(
        "/rag/documents",
        data={
            "text": "Contenido",
            "pest_label": "roya",
            "crop": "café",
            "source": "guía",
            "language": "es",
        },
        files={"file": ("guide.txt", b"Contenido", "text/plain")},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Provide exactly one of file or text"


def test_ingest_document_rejects_missing_input(
    ingest_client: tuple[TestClient, dict],
) -> None:
    client, _ = ingest_client

    response = client.post(
        "/rag/documents",
        data={
            "pest_label": "roya",
            "crop": "café",
            "source": "guía",
            "language": "es",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Provide exactly one of file or text"


def test_ingest_document_enforces_utf8_text_byte_limit(
    ingest_client: tuple[TestClient, dict],
) -> None:
    client, _ = ingest_client

    response = client.post(
        "/rag/documents",
        data={
            "text": "á" * 33,
            "pest_label": "roya",
            "crop": "café",
            "source": "guía",
            "language": "es",
        },
    )

    assert response.status_code == 413
