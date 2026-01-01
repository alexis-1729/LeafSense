from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class RecomendationCreate(BaseModel):
    title: str
    treatment_organic_id: UUID
    treatment_quimic_id: UUID

    class Config:
        orm_mode = True

class RecomendationUpdate(BaseModel):
    title: str | None = None
    treatment_quimic_id: UUID | None = None
    treatment_organic_id: UUID | None = None

class RecomendationResponse(BaseModel):
    recomendation_id: UUID
    title: str
    treatment_quimic_id: UUID
    treatment_organic_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True 