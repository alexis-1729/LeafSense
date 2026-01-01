from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class recomendacionSemanalCreate(BaseModel):
    id_semana: UUID
    tipo: str
    descripcion: str
    producto_id: UUID

class recomendacionSemanalResponse(BaseModel):
    recomendacion_id: UUID
    id_semana: UUID
    tipo: str
    descripcion: str
    producto_id: UUID
