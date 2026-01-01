from app.schemas.token import notificationCreate
from uuid import UUID
import httpx

async def send_notification(notificacion:notificationCreate, user_id: UUID):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://notification-service:8007/notification/send_token/{user_id}",
            json = notificacion.dict(),
            timeout = 5.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"Error de conexion: {e}")
        return None        
    #definir el body response