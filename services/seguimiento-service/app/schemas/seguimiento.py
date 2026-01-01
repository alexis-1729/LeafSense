from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class seguimientoCreate(BaseModel):
    diagnostico_id : UUID
    field_id: UUID
    #duracion: int

class seguimientoResponse(BaseModel):
    seguimiento_id: UUID
    diagnostico_id : UUID
    field_id: UUID
    created_at: datetime
    estado: bool 


