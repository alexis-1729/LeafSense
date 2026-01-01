from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class tokenCreate(BaseModel):
    user_id: UUID
    token: str
    last_update: datetime

class tokenResponse(BaseModel):
    user_id: UUID
    token: str
    last_update: datetime

class notificationCreate(BaseModel):
    title: str
    body: str

class notificationResponse(BaseModel):
    response: str
    message: str