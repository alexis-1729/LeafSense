from fastapi import FastAPI, File, UploadFile, APIRouter,HTTPException, Depends
from fastapi.responses import JSONResponse
from app.service.image_preprocesing import preprocess_image
from app.service.model_prediction import predict_image_class
from app.service.diagnostic_logic import save_diagnostic, get_recomendation
from app.database import get_db
from sqlalchemy.orm import Session

from PIL import Image
import io

router = APIRouter(
    prefix = "/prediction",
    tags = ["Predict"]
)

@router.post("/{username}/")
async def predict(
    username: str,
    file: UploadFile = File(...),
    db:Session = Depends(get_db)
    ):

    try:
        #lectura de imagen
        contents = await file.read()
        
        #preprocesamiento de imagen
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        processed = preprocess_image(image)

        #llamado a modelo y retorna clase
        prediction = predict_image_class(processed)

        if not prediction:
            raise HTTPException(status_code = 400, detail = "Class not clasificated")

        #guardamos el diagnostico
        await file.seek(0)
        diagnostic = await save_diagnostic(db, file, prediction, username)

        #se obtiene la recomendacion
        recomendation = await get_recomendation(prediction)

        
        return {
            "diagnostic_id": str(diagnostic.diagnostic_id),
            "fecha": diagnostic.created_at,
            "recomendacion": recomendation
        }
        
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error en diagnostico: {str(e)}")
