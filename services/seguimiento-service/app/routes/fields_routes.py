
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

from app.schemas.field import fieldCreate
from app.data.field_data import FieldData

from uuid import UUID
import logging

router = APIRouter(
    prefix = "/seguimiento/campos",
    tags = ["Campos"]
)


@router.post("/")
def create_field(data: fieldCreate, db: Session= Depends(get_db)):
    try: 
        field_data = FieldData(db)
        new = field_data.add_field(data)
        if not new:
            raise HTTPException(status_code = 500, detail = "Error en el servidor")
        return new
    except Exception as e:
        raise HTTPException(status_code = 503, detail = "Algo ocurrio en el servidor: {e}")

@router.get("/{user_id}")
def get_fields(user_id : UUID,db: Session= Depends(get_db)):
    try:
        field_data = FieldData(db)
        datos = field_data.get_fields(user_id)
        if not datos:
            raise HTTPException(status_code = 500, detail = "No se pudo obtener los registros")
        return datos
    except Exception as e:
        raise HTTPException(status_code = 503, detail = "Ocurro algo en el servidor: {e}")