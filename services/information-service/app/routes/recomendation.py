from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import  get_db
from app.services.recomendation import search_recomedation
from app.schemas.pests import RecomendationCompleteResponse
from pydantic import BaseModel
router = APIRouter(
    prefix = "/recomendation",
    tags = ["Recomendation"]
)
class ClaseRequest(BaseModel):
    clase: str

@router.post("/", response_model = RecomendationCompleteResponse)
async def recomendation(data: ClaseRequest, db:Session = Depends(get_db)):

    result = await search_recomedation(db, data.clase)

    if not result:
        raise HTTPException(status_code = 404, detail = "Clase not found")
    return result

