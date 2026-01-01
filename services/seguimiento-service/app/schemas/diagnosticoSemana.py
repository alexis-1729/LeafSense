from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class diagnosticoSemanalCreate(BaseModel):
    id_semana : UUID
    descripcion: str
    url_image: str

class diagnosticoSemanalResponse(BaseModel):
    diagS_id: UUID
    id_semana: UUID
    descripcion: str
    url_image: str