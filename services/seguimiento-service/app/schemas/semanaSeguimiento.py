from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class semanaSeguimientoCreate(BaseModel):
    id_seguimiento: UUID

class semanaSeguimientoResponse(BaseModel):
    semana_id: UUID
    id_seguimiento: UUID
    created_at: datetime

    