from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid 
from app.database import Base

class Seguimiento(Base): #followup
    __tablename__ = "seguimiento"
    seguimiento_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    diagnostico_id = Column(UUID(as_uuid = True), nullable = False)
    field_id = Column(UUID(as_uuid = True), ForeignKey("fields.id_field", ondelete = "CASCADE"), nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    #duracion = Column(Integer, nullable = False)
    estado = Column(Boolean, default = 0) #valor por default

    semana = relationship("SemanaSeguimiento", back_populates = "segui")

class SemanaSeguimiento(Base):
    __tablename__ = "semanaSeguimiento"
    semana_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    id_seguimiento = Column(UUID(as_uuid = True), ForeignKey("seguimiento.seguimiento_id", ondelete = "CASCADE"), nullable = False)
    #num_semanas = Column(Integer, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

    segui = relationship("Seguimiento", back_populates = "semana")
    diagnostic = relationship("DiagnosticoSemanal", back_populates = "sem")
    # recomendacion = relationship("RecomendacionSemanal", back_populates = "sema")
    aplication = relationship("aplication", back_populates = "semn")


class DiagnosticoSemanal(Base): #Observaciones despues de un analisis
    __tablename__ = "diagnosticoSemanal"
    diagS_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    id_semana = Column(UUID(as_uuid = True), ForeignKey("semanaSeguimiento.semana_id", ondelete = "CASCADE"), nullable = False)
    descripcion = Column(String, nullable = False)
    #severidad = Column(String, nullable = False)
    url_image = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), default = func.now())
    sem = relationship("SemanaSeguimiento", back_populates = "diagnostic")

# class RecomendacionSemanal(Base):
#     __tablename__ = "recomendacionSemanal"
#     recomendacion_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
#     id_semana = Column(UUID(as_uuid =True), ForeignKey("semanaSeguimiento.semana_id", ondelette = "CASCADE"), nullable = False)
#     tipo = Column(String, nullable = False)
#     descripcion = Column(Text, nullable = False)
#     producto_id = Column(UUID(as_uuid = True, nullable = True))
#     #checar dosis

#     sema = relationship("SemanaSeguimiento", back_populates = "recomendacion")

class aplication(Base): #Ingresa el usuario despues de aplicar 
    __tablename__ = "aplications"
    id_aplication = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    id_semana = Column(UUID(as_uuid = True), ForeignKey("semanaSeguimiento.semana_id", ondelete = "CASCADE"), nullable = False)
    product_name = Column(String, nullable = False)
    dosis_used = Column(String, nullable = True)
    dosis_unit = Column(String, nullable= False)
    notes = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), default= func.now())

    semn = relationship("SemanaSeguimiento", back_populates = "aplication")

class fields(Base):
    __tablename__ = "fields"
    id_field = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    user_id = Column(UUID(as_uuid = True), nullable = False)
    crop = Column(String, nullable = False)
    area_ha = Column(Integer, nullable = False)
    created_at = Column(DateTime(timezone= True), default = func.now())