from sqlalchemy.orm import Session
from uuid import UUID
from app.models import Recomendation
from app.schemas.recomendation import RecomendationCreate,RecomendationUpdate


def create_recomendation(db:Session, data: RecomendationCreate)-> Recomendation:
    recomendacion = Recomendation(**data.dict())
    db.add(recomendacion)
    db.commit()
    db.refresh(recomendacion)
    return recomendacion

def get_all_recomendation(db:Session)-> list[Recomendation]:
    return db.query(Recomendation).all()

def get_recomendation_by_id(db:Session, recomendation_id: UUID)-> Recomendation | None:
    return db.query(Recomendation).filter(Recomendation.recomendation_id == recomendation_id).first()

def update_recomendation(db:Session, recomendation_id: UUID, data: RecomendationUpdate)-> Recomendation | None:
    recomendacion = get_recomendation_by_id(db, recomendation_id)
    if not recomendacion:
        return None

    for key, value in data.dict(exclude_unset = True).items():
        setattr(recomendacion, key, value)
    
    db.commit()
    db.refresh(recomendacion)
    return recomendacion

def delete_recomnendation(db: Session, recomendation_id: UUID)-> bool:
    recomendacion = get_recomendation_by_id(db, recomendation_id)
    if not recomendacion:
        return False
    
    db.delete(recomendacion)
    db.commit()
    return True