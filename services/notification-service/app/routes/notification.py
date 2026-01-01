from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.data.fcm_data import FCMData
from app.services.fcm_service import FCMManager
from app.schemas.token import tokenCreate, notificationResponse, tokenResponse, notificationCreate
from uuid import UUID

router = APIRouter(
    prefix="/notification",
    tags = ["Notificaciones"]
)

@router.post("/set_token/", response_model = tokenResponse)
def set_token(data: tokenCreate, db: Session = Depends(get_db)):
    try:
        fcm_data = FCMData(db)
        token = fcm_data.set_token(data)
        if not token:
            raise HTTPException(status_code = 400, detail = "No se pudo guardaar el token")
        return token
    except Exception as e:
        raise HTTPException(status_code = 500, detail = "Error saved token {e}")

@router.get("get_token", response_model = tokenResponse)
def get_token(user_id : UUID,db: Session = Depends(get_db)):
    try:
        token_data = FCMData(db)
        token = token_data.get_token(user_id)
        return token
    except Exception as e:
        raise HTTPException(status_code = 500, detail = "Error en la obtencion del token {e}")

@router.post("/send_token/{user_id}", response_model = notificationResponse)
def send_token(user_id: UUID,data: notificationCreate, db: Session = Depends(get_db)):
    try:
        token_manager = FCMManager()
        token_data = FCMData(db)
        token = token_data.get_token(user_id)
        response = token_manager.send_message(data, token.token)
        if response.message == "Invalid token":
            token_data.delete_token(token.token)

        return response
    except Exception as e:
        raise HTTPException(status_code = 500, detail= "Error en enviar notificacion {e}")
