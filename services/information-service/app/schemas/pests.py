from pydantic import BaseModel
from datetime import datetime
from .treatment import TreatmentOrganicResponse, TreatmentQuimicResponse
from uuid import UUID
from typing import Optional, List


class ProductsResponse(BaseModel):
    name: str
    brand: str
    description: str
    ingredients: List[str]
    formulation: str
    type: str
    imageUrl: str
    

class PestsCreate(BaseModel):
    class_name: str
    name: str
    scientific_name: str
    description: str
    recomendation_id: UUID

    class Config:
        orm_mode = True

class PestsUpdate(BaseModel):
    class_name: Optional[str] = None
    name: Optional[str] = None
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    recomendation_id: Optional[UUID] = None

class PestsResponse(BaseModel):
    pest_id: UUID
    class_name: str
    name: str
    scientific_name: str
    description: str

    class Config:
        orm_mode = True

#Schemas de negocio
class RecomendationResponse(BaseModel):
    title: str
    treatment_organic: TreatmentOrganicResponse
    treatment_quimic: TreatmentQuimicResponse
    created_at: datetime

    class Config:
        orm_mode = True

class RecomendationCompleteResponse(BaseModel):
    Plage: PestsResponse
    TreatmentQuimic: TreatmentQuimicResponse
    TreatmentOrganic: TreatmentOrganicResponse
    Products: List[ProductsResponse]

    class Config:
        orm_mode =  True 




