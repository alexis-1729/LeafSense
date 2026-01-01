from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class Message(Base):
    __tablename__ = "message"
    id_message = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    sender_id = Column(UUID(as_uuid = True), nullable = True)
    reciver_id = Column(UUID(as_uuid = True), nullable = True)
    # room_id = Column(UUID(as_uuid = True), ForeignKey("room.id_room", ondelete = "CASCADE"), nullable = False)
    message = Column(Text, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

    # rm = relationship("Room", back_populates = "msg")

# class Room(Base):
#     __tablename__ = "room"
#     id_room = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
#     name = Column(String, nullable = True)
#     description = Column(String, nullable = True)
#     created_at = Column(DateTime(timezone = True), server_default = func.now())

    # msg = relationship("Message", back_populates = "rm")

class FCMToken(Base):
    __tablename__ = "fcm_token"
    id_fcm = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    user_id = Column(UUID(as_uuid = True), nullable = False)
    token = Column(String, nullable = True)
    last_update = Column(DateTime(timezone = True), server_default = func.now())

