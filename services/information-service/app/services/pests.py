from sqlalchemy.orm import Session
from app.schemas.pests import PestsCreate, PestsUpdate
from app.models import Pests
from uuid import UUID

def create_pest(db: Session, data: PestsCreate)-> Pests:
    pest = Pests(**data.dict())
    db.add(pest)
    db.commit()
    db.refresh(pest)
    return pest

def get_all_pests(db: Session)-> list[Pests]:
    return db.query(Pests).all()

def get_pest_by_id(db:Session, pest_id:UUID )-> Pests | None:
    return db.query(Pests).filter(Pests.pest_id == pest_id).first()

def update_pest(db:Session, pest_id: UUID, data: PestsUpdate)-> Pests| None:
    pest = get_pest_by_id(db, pest_id)
    if not pest:
        return None
    for key, value in data.dict(exclude_unset = True).items():
        setattr(pest, key, value)

    db.commit()
    db.refresh(pest)
    return pest

def delete_pest(db: Session, pest_id: UUID)-> bool:
    pest = get_pest_by_id(db, pest_id)
    
    if not pest:
        return False
    
    db.delete(pest)
    db.commit()

    return True

