from sqlalchemy.orm import Session
from app.models import Treatment_quimic, Treatment_organic
from uuid import UUID
from app.schemas.treatment import *

def create_organic(db: Session, data: TreatmentOrganicCreate) -> Treatment_organic:
    treatment = Treatment_organic(**data.dict())
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment

def get_all_organic(db: Session)-> list[Treatment_organic]:
    return db.query(Treatment_organic).all()

def get_organic_by_id(db: Session, id_: UUID)-> Treatment_organic | None:
    return db.query(Treatment_organic).filter(Treatment_organic.organic_id == id_).first()

def update_organic(db: Session, id_: UUID, data: TreatmentOrganicUpdate)-> Treatment_organic | None:
    treatment = get_organic_by_id(db, id_)
    if not treatment:
        return None

    for key, value in data.dict(exclude_unset =  True).items():
        setattr(treatment, key, value)
    
    db.commit()
    db.refresh(treatment)
    return treatment

def delete_organic(db: Session, id_: UUID)-> bool:
    treatment = get_organic_by_id(db, id_)
    if not treatment:
        return False

    db.delete(treatment)
    db.commit()
    return True

#---------Quimic-----------------

def create_quimic(db: Session, data: TreatmentQuimicCreate) -> Treatment_quimic:
    treatment = Treatment_quimic(**data.dict())
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment

def get_all_quimic(db: Session)-> list[Treatment_quimic]:
    return db.query(Treatment_quimic).all()

def get_quimic_by_id(db: Session, id_: UUID)-> Treatment_quimic | None:
    return db.query(Treatment_quimic).filter(Treatment_quimic.quimic_id == id_).first()

def update_quimic(db: Session, id_: UUID, data: TreatmentQuimicUpdate)-> Treatment_quimic | None:
    treatment = get_quimic_by_id(db, id_)
    if not treatment:
        return None

    for key, value in data.dict(exclude_unset =  True).items():
        setattr(treatment, key, value)
    
    db.commit()
    db.refresh(treatment)
    return treatment

def delete_quimic(db: Session, id_: UUID)-> bool:
    treatment = get_quimic_by_id(db, id_)
    if not treatment:
        return False

    db.delete(treatment)
    db.commit()
    return True