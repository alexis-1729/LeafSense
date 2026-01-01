from sqlalchemy.orm import Session
from uuid import UUID
import logging
from app.schemas.aplication import aplicationCreate, aplicationResponse
from app.models import aplication

class AplicationData:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("AplicationData")
    
    def add_aplication(self, data: aplicationCreate)-> aplicationResponse | None:
        try:
            new = aplication(**data.dict())

            self.db.add(new)
            self.db.commit()
            self.db.refresh(new)
            return new
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error en el registro: {e}")
            return None