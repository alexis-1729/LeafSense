from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class fieldCreate(BaseModel):
    user_id : UUID
    crop: str
    area_ha: int

class fieldResponse(BaseModel):
    id_field: UUID
    user_id: UUID
    crop: str
    are_ha: int
    created_at: datetime

