from typing import Annotated
from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from app.api.deps import AdminClaims, get_connection
from app.core.config import Settings
from app.infrastructure.persistence.document_repo import DocumentRepository
from app.schemas.documents import DocumentCreated, DocumentStatusResponse

router = APIRouter(prefix="/rag/documents", tags=["documents"])


async def _read_limited(file: UploadFile, max_bytes: int) -> bytes:
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Document exceeds the {max_bytes}-byte limit",
        )
    return content


@router.post("", response_model=DocumentCreated, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    request: Request,
    _: AdminClaims,
    pest_label: Annotated[str, Form(min_length=1, max_length=100)],
    crop: Annotated[str, Form(min_length=1, max_length=100)],
    source: Annotated[str, Form(min_length=1, max_length=300)],
    language: Annotated[str, Form(min_length=2, max_length=12)],
    connection: Annotated[psycopg.Connection, Depends(get_connection)],
    file: Annotated[UploadFile | None, File()] = None,
    text: Annotated[str | None, Form(min_length=1)] = None,
) -> DocumentCreated:
    settings: Settings = request.app.state.settings
    if (file is None) == (text is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide exactly one of file or text",
        )

    if file is not None:
        filename = file.filename or "document.txt"
        extension = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
        if extension not in {"txt", "md", "pdf"}:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only plain text, Markdown, and PDF documents are supported",
            )
        content = await _read_limited(file, settings.max_document_bytes)
        try:
            document_text = request.app.state.document_extractor.extract(content, extension)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
    else:
        filename = "document.txt"
        if text is None:
            raise RuntimeError("Document input validation did not select an input")
        if len(text.encode("utf-8")) > settings.max_document_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Document exceeds the {settings.max_document_bytes}-byte limit",
            )
        document_text = text

    if not document_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document contains no extractable text",
        )
    metadata = {
        "pest_label": pest_label.strip(),
        "crop": crop.strip(),
        "source": source.strip(),
        "language": language.strip().lower(),
    }
    if not all(metadata.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document metadata fields must not be blank",
        )

    repository = DocumentRepository(connection)
    document = repository.create(
        text=document_text,
        **metadata,
        filename=filename[:300],
    )
    return DocumentCreated(id=document["id"], status=document["status"])


@router.get("/{document_id}", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: UUID,
    _: AdminClaims,
    connection: Annotated[psycopg.Connection, Depends(get_connection)],
) -> DocumentStatusResponse:
    document = DocumentRepository(connection).get_status(document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return DocumentStatusResponse(**document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    request: Request,
    _: AdminClaims,
    connection: Annotated[psycopg.Connection, Depends(get_connection)],
) -> None:
    repository = DocumentRepository(connection)
    document = repository.mark_deleting(document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    try:
        request.app.state.vector_store.delete_document(document_id)
    except Exception:
        repository.restore_status(document_id, document["status"])
        raise
    repository.delete(document_id)
