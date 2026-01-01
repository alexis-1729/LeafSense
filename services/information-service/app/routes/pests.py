from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from uuid import UUID
from app.schemas.pests import PestsCreate, PestsResponse, PestsUpdate
from app.services.pests import *

router = APIRouter(
    prefix = "/admin/pests",
    tags=["Admin - Plagas"]
)

@router.post("/", response_model = PestsResponse)
def create_pest_route(data: PestsCreate, db:Session = Depends(get_db)):
    return create_pest(db, data)

@router.get("/", response_model = list[PestsResponse])
def get_all_pest_route(db: Session = Depends(get_db)):
    return get_all_pests(db)

@router.get("/{pest_id}", response_model = PestsResponse)
def get_pest_by_id_route(pest_id: UUID, db: Session = Depends(get_db)):
    pest = get_pest_by_id(db, pest_id)
    if not pest:
        raise HTTPException(status_code = 404, detail = "Pest not found")
    return pest

@router.put("/{pest_id}", response_model = PestsResponse)
def update_pest_route(pest_id: UUID, data: PestsUpdate, db: Session = Depends(get_db),):
    pest = update_pest(db, pest_id, data)
    if not pest:
        raise HTTPException(status_code = 404, detail= "Pest not found")
    return pest

@router.delete("/{pest_id}")
def delete_pest_route(pest_id: UUID,db: Session = Depends(get_db)):
    success = delete_pest(db, pest_id)
    if not success:
        raise HTTPException(status_code = 404, detail = "Pest not found")
    return {"detail": "success"}
    