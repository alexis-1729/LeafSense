from sqlalchemy.orm import Session, joinedload
from app.models import Pests, Recomendation, Treatment_quimic, Treatment_organic
from app.schemas.pests import PestsResponse,   RecomendationCompleteResponse, ProductsResponse
from app.schemas.treatment import TreatmentQuimicResponse,  TreatmentOrganicResponse
from typing import List
import httpx
async def get_products(clase: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://products-service:8084/api/product/by-target/{clase}",
            timeout= 5.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"Error de conexion o HTTP: {e}")
        return None


async def search_recomedation(db:Session, class_name: str)-> RecomendationCompleteResponse | None:
    pest = db.query(Pests).options(
        joinedload(Pests.recomendation)
            .joinedload(Recomendation.treatment_quimic),
        joinedload(Pests.recomendation)
            .joinedload(Recomendation.treatment_organic)
    ).filter(Pests.class_name == class_name).first()

    if not pest or not pest.recomendation:
        return None
    
    products = await get_products(class_name)

    return RecomendationCompleteResponse(
        Plage = PestsResponse(
            pest_id= pest.pest_id,
            class_name=pest.class_name,
            name= pest.name,
            scientific_name= pest.scientific_name,
            description= pest.description
        ),
        TreatmentQuimic=TreatmentQuimicResponse(
            quimic_id= pest.recomendation.treatment_quimic.quimic_id,
            dose= pest.recomendation.treatment_quimic.dose,
            frequency= pest.recomendation.treatment_quimic.frequency,
            toxycity= pest.recomendation.treatment_quimic.toxycity,
            observations= pest.recomendation.treatment_quimic.observations,
            fuente= pest.recomendation.treatment_quimic.fuente
        ),
        TreatmentOrganic=TreatmentOrganicResponse(
            organic_id = pest.recomendation.treatment_organic.organic_id,
            aplication= pest.recomendation.treatment_organic.aplication,
            frequency= pest.recomendation.treatment_organic.frequency,
            observations= pest.recomendation.treatment_organic.observations,
            fuente= pest.recomendation.treatment_organic.fuente
        ),
        Products=[ProductsResponse(**p) for p in products] if products else []

    )

