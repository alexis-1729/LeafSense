from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.treatment import *
from app.services.admin_treatment import *

router = APIRouter (
    prefix ="/admin/treatments",
    tags = ["Admin Treatments"]
)

@router.post("/organic", response_model = TreatmentOrganicResponse)
def create_organic_route( data: TreatmentOrganicCreate, db: Session = Depends(get_db)):
    return create_organic(db, data)

@router.get("/organic", response_model = list[TreatmentOrganicResponse])
def get_organics_route(db: Session = Depends(get_db)):
    return get_all_organic(db)

@router.get("/organic/{id_}", response_model = TreatmentOrganicResponse)
def get_organic_route( id_: UUID, db: Session = Depends(get_db)):
    organic = get_organic_by_id(db,id_)
    if not organic:
        raise HTTPException(status_code = 404, detail = "Organic not found")
    
    return organic

@router.put("/organic/{id_}", response_model = TreatmentOrganicResponse)
def update_organic_route(id_: UUID, data: TreatmentOrganicUpdate, db: Session = Depends(get_db)):
    organic = update_organic(db,id_, data)
    if not organic:
        raise HTTPException(status_code = 404, detail = "Organic not found")
    return organic
    
@router.delete("/organic/{id_}")
def delete_organic_route(id_: UUID, db: Session = Depends(get_db)):
    if not delete_organic(db,id_):
        raise HTTPException(status_code = 404, detail = "Organic not found")
    return {"detail": "success"}

#-------------Quimic------------------
@router.post("/quimic", response_model = TreatmentQuimicResponse)
def create_quimic_route( data: TreatmentQuimicCreate,db: Session = Depends(get_db)):
    return create_quimic(db, data)

@router.get("/quimic", response_model = list[TreatmentQuimicResponse])
def get_quimics_route(db: Session = Depends(get_db)):
    return get_all_quimic(db)

@router.get("/quimic/{id_}", response_model = TreatmentQuimicResponse)
def get_quimic_route(id_: UUID, db: Session = Depends(get_db)):
    quimic = get_quimic_by_id(db,id_)
    if not quimic:
        raise HTTPException(status_code = 404, detail = "quimic not found")
    
    return quimic

@router.put("/quimic/{id_}", response_model = TreatmentQuimicResponse)
def update_quimic_route(id_: UUID, data: TreatmentQuimicUpdate, db: Session = Depends(get_db)):
    quimic = update_quimic(db,id_, data)
    if not quimic:
        raise HTTPException(status_code = 404, detail = "quimic not found")
    return quimic

@router.delete("/quimic/{id_}")
def delete_quimic_route(id_: UUID, db: Session = Depends(get_db)):
    if not delete_quimic(db, id_):
        raise HTTPException(status_code = 404, detail = "quimic not found")
    return {"detail": "success"}
