import firebase_admin
from firebase_admin import credentials, messaging
from uuid import UUID
from app.models import FCMToken
from app.schemas.token import notificationCreate, notificationResponse
import logging

class FCMManager:
    def __init__(self):
        self.logger = logging.getLogger("FCMService")

    def send_message(self, data: notificationCreate, token: str):
        if not token:
            self.logger.error(f"Error not token in db")
            return notificationResponse(
                response = "error",
                message = "Not found token"
            )
        
        message = messaging.Message(
            notification = messaging.Notification(
                title = data.title, 
                body = data.body
                ),
            token = token,
            data = {}
        )

        try:
            response = messaging.send(message)
            self.logger.info(f"Succes in send message")
            return notificationResponse(
                response = "success",
                message = response
            )
        except messaging.UnregisteredError:
            self.logger.error(f"Invalid token")
            return notificationResponse(
                response = "error",
                message = "Invalid token"
            )
        except Exception as e:
            self.logger.error(f"Error in send message: {e}")
            return notificationResponse(
                response = "error",
                message = "Error en el envio de notificaciones"
            ) 