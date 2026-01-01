from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from app.schemas.message import messageCreate, messageResponse
from app.models import Message
from app.data.message import MessageData
from app.services.fcm_notifications import send_notification
from app.schemas.token import notificationCreate
from uuid import UUID
import logging

class MessagingManager:

    # creamos e inicializamos la instancia self de la clase 
    def __init__(self):
        self.active_connections: dict[UUID,WebSocket] = {}
        self.logger = logging.getLogger("MessagingManager")
    
    async def connect(self, websocket: WebSocket, user_id: UUID):
        self.logger.info(f"intentando coneccion")
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: UUID):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            self.logger.info(f"Usuario {user_id} desconectado")
    
    #detalle de conversion
    async def send_message_to(self, message:messageResponse, user_id: UUID):
        
        try:
            receiver = self.active_connections.get(message.reciver_id)

            json_message = jsonable_encoder(message)
            if receiver:

                self.logger.info(f"Enviando mensaje a {message.reciver_id} por ws")
                await receiver.send_json(json_message)
                return True
            else : 
                noti = await send_notification(
                        notificationCreate(
                            title = "Nuevo Mensaje",
                            body = message.message
                        ),user_id
                    )
            
                if noti:
                    if noti.response == "success":
                        self.logger.info("Se envio una notificacion")
                        return noti
                    else:
                        self.logger.info(f"error in the send notification") 
                        return None
                else:
                    self.logger.info(f"Error en el envio  de la notificacion {message.reciver_id}")
                    return None
        except Exception as e:
            self.logger.info(f"Error durante el envio de mensaje {e}")
    
    # async def broadcast(self, message: messageResponse, room_id: UUID):
    #     try:

    #         if room_id in self.active_connections:
    #             self.logger.info(
    #                 f"Broadcasting message to {len(self.active_connections[room_id])} clients"
    #             )
    #         for connection in self.active_connections[room_id]:
    #             await self.send_message_to(connection, message)

    #         #logica de enviar notiificaciones

    #         # self.fcm_service.send_notification(
    #         #     target_user_id=message.user_id,
    #         #     title="Nuevo mensaje",
    #         #     body=message.message,
    #         #     data={"room_id": message.room_id, "message_id": message.message_id},
    #         # )
    #     except Exception as e:
    #         self.logger.error(f"Error broadcasting message: {e}")
        


