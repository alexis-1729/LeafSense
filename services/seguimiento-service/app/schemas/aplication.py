from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class aplicationCreate(BaseModel):
    id_semana: UUID
    product_name: str
    dosis_used: str | None = None
    dosis_unit: str | None = None
    notes: str

class aplicationResponse(BaseModel):
    id_semana: UUID
    product_name: str
    dosis_used: str | None = None
    dosis_unit: str | None = None
    notes: str
    created_at: datetime