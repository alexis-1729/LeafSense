from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PestScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class DiagnosisContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=2000)
    severity: Literal["low", "medium", "high", "unknown"]
    recommendations: list[str] = Field(max_length=8)
    limitations: list[str] = Field(max_length=8)


class DiagnosisSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    source: str
    crop: str
    language: str
    score: float
    excerpt: str


class DiagnosisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    pest_label: str
    confidence: float = Field(ge=0.0, le=1.0)
    top_k: list[PestScore]
    conclusive: bool
    diagnosis: DiagnosisContent | None
    message: str | None
    sources: list[DiagnosisSource]
