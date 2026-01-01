from sqlalchemy.orm import Session
from uuid import UUID
import logging

from app.schemas.recomendacionesSemanal import recomendacionSemanalCreate, recomendacionSemanalResponse
from app.models import RecomendacionSemanal

class RecomendacionData:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("RecomendacionData")
    
    def add_recomendacion(self, data: recomendacionSemanalCreate):
        try:
            new = RecomendacionSemanal(**data.dict())
            self.db.add(new)
            self.db.commit()
            self.db.refresh(new)
            return new
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating recomendacion")
            return None
    
    def get_Recomendacion(self, id_semana : UUID)-> list[recomendacionSemanalResponse]:
        try:
            recomendacion = self.db.query(RecomendacionSemanal).filter(RecomendacionSemanal.id_semana == id_semana).all()
            if recomendacion:
                  return recomendacion
            else:
                  self.logger.error(f"Operacion fallida: {e}")
                  return None
        except Exception as e:
              self.logger.info(f"Error op get recomendacion: {e}")
              return None