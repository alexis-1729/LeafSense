from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InternalUserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    email: EmailStr


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, min_length=1, max_length=100)


class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    display_name: str | None
    created_at: datetime
    updated_at: datetime
