from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .database import Base

class Image(Base):
    __tablename__ = "image"
    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    diagnostic = relationship("Diagnostic", back_populates="image", uselist=False)

class Diagnostic(Base):
    __tablename__ = "diagnostic"
    diagnostic_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("image.image_id", ondelete="CASCADE"), nullable=False)
    clase = Column(Text, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    image = relationship("Image", back_populates="diagnostic")