from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentCreated(BaseModel):
    id: UUID
    status: str


class DocumentStatusResponse(BaseModel):
    id: UUID
    pest_label: str
    crop: str
    source: str
    language: str
    filename: str
    status: str
    chunk_count: int
    error: str | None
    created_at: datetime
    updated_at: datetime
