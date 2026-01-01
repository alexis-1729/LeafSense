from fastapi import  WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.manager_message import MessagingManager
# from app.services.manager_rooms import RoomsManager
from app.data.message import MessageData
# from app.data.room import RoomsData
# from app.schemas.room import roomCreate
from app.schemas.message import messageCreate
from app.models import Message
import asyncio
from uuid import UUID
import logging 


router = APIRouter(
    prefix = "/rooms",
    tags = ["Rooms"]
)

api_logger = logging.getLogger("API")

# rooms_manager = RoomsManager()
chat_manager = MessagingManager()



@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID, db: Session = Depends(get_db)):
    await chat_manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()
            
            new_message = messageCreate(
                sender_id = data["sender_id"],
                reciver_id = data["reciver_id"],
                message = data["message"]
            )    
            message_data = MessageData(db)
            new_m = message_data.add_message(new_message)
            if new_m: 
               ans = await chat_manager.send_message_to(new_m, user_id)
               if not ans:
                   print(f"fallo el envio de notificacion")
               else: 
                   api_logger.info("Se envio la norificacion")
                   
            else: 
                print("NO se pudo agregar")
    except WebSocketDisconnect:
         api_logger.info("Client disconnected")
         chat_manager.disconnect(user_id)

@router.get("/get_message/{user_id}/{user_id2}")
def get_message(user_id : UUID, user_id2: UUID, db: Session  = Depends(get_db)):
    try:
        message_data = MessageData(db)
        messages = message_data.get_messages(user_id, user_id2)
        if messages:
            api_logger.info("get messages")
            return messages
        else:
            api_logger.info("not messages")
    except Exception as e:
        api_logger.error("Error getting message: {e}")


@router.get("/messages/{user_id}")
def messages(user_id : UUID, db: Session  = Depends(get_db)):
    try:
        message_data = MessageData(db)
        messages = message_data.get_message(user_id)
        if messages:
            api_logger.info("get messages")
            return messages
        else:
            api_logger.info("not messages")
    except Exception as e:
        api_logger.error("Error getting message: {e}")
        
# @router.post("/add-room/")
# async def handle_add_room(room: roomCreate, db: Session = Depends(get_db)):
#     rooms_data = RoomsData(db)
#     new_room = rooms_data.add_room(room)
#     if new_room:
#         await rooms_manager.broadcast_room(new_room)
#         return {"message": "Room added"}
#     raise HTTPException(status_code = 500, detail = "Error adding room")

# @router.websocket("/rooms_conecction/")
# async def handle_new_conecction_rooms(websocket: WebSocket, db: Session = Depends(get_db)):
#     try:
#         await rooms_manager.add_rooms_listener(websocket)
#         rooms_data = RoomsData(db)
#         rooms = rooms_data.get_all_rooms()
        
#         api_logger.info(f"Sending rooms: {len(rooms)}")

#         for room in rooms:
#             await rooms_manager.send_room_to(websocket, room)
        
#         while True:
#             await asyncio.sleep(1)

#     except WebSocketDisconnect as e:
#         await rooms_manager.remove_room(websocket)

# @router.websocket("/connect-rooms/{room_id}")
# async def handle_connect_to_room(websocket: WebSocket, room_id: UUID, db: Session = Depends(get_db)):
#     #conectamos el cliente
#     print(f"Intentando coneccion: {room_id}")
#     await chat_manager.connect(websocket, room_id)
#     messages_data = MessageData(db)
#     messages = messages_data.get_message_of(room_id)

#     for message in messages:
#         api_logger.info(f"Sending message to new client")
#         await chat_manager.send_message_to(websocket, message)

#     try:
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
#     except WebSocketDisconnect:
#         api_logger.info("Client disconnected")
#         chat_manager.disconnect(websocket, room_id)





