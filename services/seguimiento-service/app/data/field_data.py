from sqlalchemy.orm import Session
import logging
from app.schemas.field import fieldCreate, fieldResponse
from app.models import fields
from uuid import UUID
class FieldData:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("FieldData")

    def add_field(self,data: fieldCreate)-> fieldResponse | None:
        try:
            new = fields(**data.dict())
            self.db.add(new)
            self.db.commit() 
            self.db.refresh(new)
            return new
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error en la creacion del nuevo registro: {e}")
            return None
    
    def get_fields(self, user_id: UUID)-> list[fieldResponse]:
        try:
            datos = self.db.query(fields).filter(fields.user_id == user_id).all()
            if not datos:
                return None
            return datos
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Ocurrio un problema: {e}")
            return None

