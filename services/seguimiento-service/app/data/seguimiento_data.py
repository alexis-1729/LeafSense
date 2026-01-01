from sqlalchemy.orm import Session
from app.models import Seguimiento
from app.schemas.seguimiento import seguimientoCreate, seguimientoResponse
import logging
from uuid import UUID
class SeguimientoData:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("SeguimientoData")      
    
    def add_seguimiento(self, data: seguimientoCreate):
        try:
            new = Seguimiento(**data.dict())
            self.db.add(new)
            self.db.commit()
            self.db.refresh(new)
            return new
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error adding new seguimiento: {e}")
            return None
        
    def get_seguimiento(self, diagnostico_id : UUID)-> seguimientoResponse:
        try:
            seguimiento = self.db.query(Seguimiento).filter(Seguimiento.diagnostico_id == diagnostico_id).all()
            if seguimiento:
                  return seguimiento
            else:
                  self.logger.error(f"Operacion fallida: {e}")
                  return None
        except Exception as e:
              self.logger.info(f"Error op get seguimiento: {e}")
              return None
    
    def delete_seguimiento(self, diagnostico_id: UUID):
        try: 
            seguimiento = self.db.query(Seguimiento).filter(Seguimiento.diagnostico_id == diagnostico_id).first()
            self.db.delete(seguimiento)
            self.db.commit()
            return {"response": "success", "msg":"Eliminated"}
        except Exception as e:
            self.db.rollback()
            self.logger.error(f" Error with elimination of seguimiento")
            return {"response": "error", "msg":"Cant Eliminated"}
