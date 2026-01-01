from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class crops_create(BaseModel):
    name_common: str
    scientific_name: str

    class Config:
        orm_mode = True

class crops_response(BaseModel):
    crop_id: UUID
    name_common: str
    scientific_name: str
    created_at: datetime

    class Config:
        orm_mode = True







