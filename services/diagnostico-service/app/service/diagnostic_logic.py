import httpx
from app.database import get_db
from app.models import Diagnostic, Image
from sqlalchemy.orm  import Session
from fastapi import UploadFile, File, HTTPException
import os
from uuid import uuid4

UPLOAD_DIR = "app/uploads"

async def get_recomendation(clase: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://information-service:8001/recomendation/", 
            json = {"clase": clase},
            timeout= 10.0
            )
            if response.status_code == 404:
                raise HTTPException(status_code= 404, detail = "Recomendation not found")
            elif response.status_code != 200:
                raise HTTPException(status_code = 500, detail ="Error service")

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code = 503, detail = f"Conection failed: {str(e)}")

    
#guardamos diagnostico

async def save_diagnostic(db: Session, image_file: UploadFile, class_name: str, username: str)-> Diagnostic:
    image_id = uuid4()
    extension = os.path.splitext(image_file.filename)[-1]
    filename = f"{image_id}{extension}"

    path = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok = True)

    with open(path, "wb") as f:
        f.write(await image_file.read())
    
    image_record = Image(image_id = image_id, url = path)
    db.add(image_record)
    db.flush()

    diagnostic_record = Diagnostic(
        image_id = image_id,
        clase = class_name,
        username = username
    )

    db.add(diagnostic_record)
    db.commit()
    db.refresh(diagnostic_record)

    return diagnostic_record
