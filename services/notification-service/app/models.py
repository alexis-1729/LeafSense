from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class FCMToken(Base):
    __tablename__ = "fcm_token"
    id_token = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    user_id = Column(UUID(as_uuid = True), nullable = False)
    token = Column(String, nullable = True)
    last_update = Column(DateTime(timezone = True), server_default = func.now())

