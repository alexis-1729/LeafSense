from sqlalchemy.orm import Session
from uuid import UUID
import logging
from app.schemas.semanaSeguimiento import semanaSeguimientoCreate, semanaSeguimientoResponse
from app.models import SemanaSeguimiento

class SemanaData:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("SemanaData")
    
    def add_semana(self, data: semanaSeguimientoCreate):
        try:
            new = SemanaSeguimiento(**data.dict())
            self.db.add(new)
            self.db.commit()
            self.db.refresh(new)
            return new
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error create new semana: {e}")
            return None
        
    def get_Semana(self, id_seguimiento : UUID)-> semanaSeguimientoResponse:
        try:
            semana = self.db.query(SemanaSeguimiento).filter(SemanaSeguimiento.id_seguimiento == id_seguimiento).first()
            if semana:
                  return semana
            else:
                  self.logger.error(f"Operacion fallida: {e}")
                  return None
        except Exception as e:
              self.logger.info(f"Error op get semana: {e}")
              return None
    
