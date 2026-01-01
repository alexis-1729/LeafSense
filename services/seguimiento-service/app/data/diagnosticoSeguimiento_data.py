from sqlalchemy.orm import Session
from uuid import UUID
import logging

from app.schemas.diagnosticoSemana import diagnosticoSemanalCreate, diagnosticoSemanalResponse
from app.models import DiagnosticoSemanal

class DiagnosticoData:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("DiagnosticoData")
    
    def add_diagnostico(self, data: diagnosticoSemanalCreate):
        try:
            new = DiagnosticoSemanal(**data.dict())
            self.db.add(new)
            self.db.commit()
            self.db.refresh(new)
            return new
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error create new diagnostico: {e}")
            return None
    
    def get_Diagnostico(self, id_semana : UUID)-> list[diagnosticoSemanalResponse]:
        try:
            diagnostico = self.db.query(DiagnosticoSemanal).filter(DiagnosticoSemanal.id_semana == id_semana).all()
            if diagnostico:
                  return diagnostico
            else:
                  self.logger.error(f"Operacion fallida: {e}")
                  return None
        except Exception as e:
              self.logger.info(f"Error op get diagnostico: {e}")
              return None