from pydantic import BaseModel
from uuid import UUID

class ImageCreate(BaseModel):
    url: str

    class Config:
        orm_mode = True

class ImageResponse(BaseModel):
    url: str

    class Config:
        orm_mode = True

class DiagnosticCreate(BaseModel):
    image_id: UUID
    recommendation_id: UUID
    description: str
    severidad: str

    class Config:
        orm_mode = True

class DiagnosticResponse(BaseModel):
    diagnostic_id: UUID
    image_id: UUID
    recommendation_id: UUID
    description: str
    severidad: str

    class Config:
        orm_mode = True