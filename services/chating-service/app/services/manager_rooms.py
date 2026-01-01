# from app.schemas.room import roomCreate, roomResponse
# from app.data.room import RoomsData
# from fastapi import WebSocket
# from fastapi.encoders import jsonable_encoder
# import logging 

# class RoomsManager:
#     def __init__(self): 
#         self.rooms_listeners: set[WebSocket] = set([])
#         self.logger = logging.getLogger("RoomsManager")
        
#     async def add_rooms_listener(self, websocket: WebSocket):
#         await websocket.accept()
#         self.rooms_listeners.add(websocket)
    
#     async def send_room_to(self, websocket: WebSocket, room: roomResponse):
#         json_room = jsonable_encoder(room)
#         await websocket.send_json(json_room)
        
#     async def remove_room(self, websocket: WebSocket):
#         self.rooms_listeners.remove(websocket)

#     async def broadcast_room(self, room: roomResponse):
#         try:
#             #conversion
#             json_room = jsonable_encoder(room)
#             for client in list(self.rooms_listeners):
#                 try:
#                     await client.send_json(json_room)
#                 except Exception:
#                     self.rooms_listeners.remove(client)
            
#             self.logger.info(f"Broadcast room {room.name}")

#         except Exception as e:
#             self.logger.error(f"Error broadcasting room: {e}")