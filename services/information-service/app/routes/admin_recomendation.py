from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.recomendation import (
    RecomendationCreate,
    RecomendationUpdate,
    RecomendationResponse
)
from app.services.admin_recomendation import *
from app.database import get_db

router = APIRouter(
    prefix = "/admin/recomnedation",
    tags = ["Admin Recomendaciones"]
)

@router.post("/", response_model = RecomendationResponse)
def create_recomendation_route( data: RecomendationCreate, db: Session = Depends(get_db)):
    return create_recomendation(db, data)

@router.get("/", response_model = list[RecomendationResponse])
def get_all_recomendation_route(db:Session = Depends(get_db)):
    return get_all_recomendation(db)

@router.get("/{recomendation_id}", response_model = RecomendationResponse)
def get_recomendation_by_id_route( recomendation_id: UUID,db: Session = Depends(get_db)):
    recomendation = get_recomendation_by_id(db, recomendation_id)
    if not recomendation:
        raise HTTPException(status_code = 404, detail= "Recomendation not found")
    return recomendation

@router.put("/{recomendation_id}", response_model = RecomendationResponse)
def update_recomendation_route(recomendation_id: UUID,  data: RecomendationUpdate, db: Session = Depends(get_db)):
    recomendacion = update_recomendation(db, recomendation_id, data)
    if not recomendacion:
        raise HTTPException(status_code = 404, detail = "Recomendation not found")
    return recomendacion

@router.delete("/{recomendation_id}")
def delete_recomnendations_route(recomendation_id: UUID,db: Session =  Depends(get_db)):
    success = delete_recomnendation(db, recomendation_id)
    if not success:
        raise HTTPException(status_code = 404, detail = "Recomendation not found")
    return {"detail": "success"}

