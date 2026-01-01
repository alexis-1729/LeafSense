from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class messageCreate(BaseModel):
    sender_id: UUID #user_id de la persona
    reciver_id: UUID #user_id del profesional
    message: str

class messageResponse(BaseModel):
    id_message: UUID
    sender_id: UUID
    reciver_id: UUID
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

#  try:
#         while True:
#             data = await websocket.receive_json()
#             api_logger(f"Receive {data}")

#             if "type" in data and data["type"] == "close":
#                 chat_manager.disconnect(websocket, room_id)
#             else:
#                 message = messageCreate(
#                     sender_id = data["sender_id"],
#                     reciver_id = data["reciver_id"],
#                     room_id = data["room_id"],
#                     message = data["message"]
#                 )
#                 messages_data.add_message(message)
#                 await chat_manager.broadcast(message, room_id)