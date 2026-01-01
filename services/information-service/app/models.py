from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid 
from app.database import Base

class crops(Base):
    __tablename__ = "crops"
    crop_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    name_common =Column(String, unique = True, index = True)
    scientific_name = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

class Pests(Base):
    __tablename__ = "pests_info"
    pest_id = Column(UUID(as_uuid =  True), primary_key =  True, default = uuid.uuid4)
    class_name = Column(String, nullable =  False)
    name = Column(String, nullable =  False)
    scientific_name = Column(String, nullable = False)
    recomendation_id = Column(UUID(as_uuid = True), ForeignKey("recomendation.recomendation_id", ondelete = "CASCADE"), nullable = False)
    description = Column(String, nullable =  False)

    recomendation = relationship("Recomendation", back_populates = "pest")

class Recomendation(Base):
    __tablename__ = "recomendation"

    recomendation_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    title = Column(String, nullable =  False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

    treatment_quimic_id = Column(UUID(as_uuid = True), ForeignKey("treatment_quimic.quimic_id", ondelete = "CASCADE"),  nullable = False)
    treatment_quimic = relationship("Treatment_quimic", back_populates = "recomendations")

    treatment_organic_id = Column(UUID(as_uuid = True), ForeignKey("treatment_organic.organic_id", ondelete = "CASCADE"), nullable = False)
    treatment_organic = relationship("Treatment_organic", back_populates = "recomendations")

    pest = relationship("Pests", back_populates = "recomendation", cascade = "all, delete-orphan")

class Treatment_quimic(Base):
    __tablename__ = "treatment_quimic"
    quimic_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    id_product =  Column(UUID(as_uuid = True), nullable = True)
    dose = Column(String, nullable = False)
    frequency = Column(String, nullable = False)
    toxycity = Column(String, nullable = False)
    observations = Column(String, nullable = False)
    fuente = Column(String, nullable = True)

    recomendations = relationship("Recomendation", back_populates = "treatment_quimic")

class Treatment_organic(Base):
    __tablename__ = "treatment_organic"
    organic_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    id_product =  Column(UUID(as_uuid = True))
    aplication = Column(String, nullable = False)
    frequency = Column(String, nullable = False)
    observations = Column(String, nullable = False)
    fuente = Column(String, nullable = False)

    recomendations = relationship("Recomendation", back_populates = "treatment_organic")




    
