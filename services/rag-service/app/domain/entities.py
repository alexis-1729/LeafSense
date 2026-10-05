from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Document:
    id: UUID
    pest_label: str
    crop: str
    source: str
    language: str
    filename: str
    status: str
    error: str | None
    created_at: datetime
    updated_at: datetime
