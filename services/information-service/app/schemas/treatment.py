from pydantic import BaseModel
from uuid import UUID

class TreatmentOrganicCreate(BaseModel):
    aplication: str
    frequency: str
    observations: str
    fuente: str

    class Config:
        orm_mode = True

class TreatmentOrganicUpdate(BaseModel):
    aplication: str | None = None
    frequency: str | None = None
    observations: str | None = None
    fuente: str | None = None


class TreatmentOrganicResponse(BaseModel):
    organic_id: UUID
    aplication: str
    frequency: str
    observations: str
    fuente: str
    
    class Config:
        orm_mode = True

class TreatmentQuimicCreate(BaseModel):
    id_product: UUID | None = None
    dose: str
    frequency: str
    toxycity: str
    observations: str
    fuente: str

class TreatmentQuimicUpdate(BaseModel):
    id_product: UUID | None = None
    dose: str | None = None
    frequency: str | None = None
    toxycity: str | None = None
    observations: str | None = None
    fuente: str | None = None

class TreatmentQuimicResponse(BaseModel):
    quimic_id: UUID
    dose: str
    frequency: str
    toxycity: str
    observations: str
    fuente: str

    class Config: 
        orm_mode = True


