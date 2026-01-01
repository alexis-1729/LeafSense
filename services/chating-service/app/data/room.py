# from sqlalchemy.orm import Session
# from app.schemas.room import *
# from app.models import Room
# import logging

# class RoomsData:

#     def __init__(self, db: Session):
#         self.db = db
#         self.logger = logging.getLogger("RoomsData")

#         general = Room(
#             name = "General",
#             description = "General room"
#             )
#         self.add_room(general)

#     def add_room(self, room: roomCreate)-> roomResponse | None:
#         try:
#             db_room = (
#                 self.db.query(Room)
#                 .filter(Room.name == room.name)
#                 .first()
#             )

#             if db_room:
#                 db_room.description = room.description
#             else:
#                 db_room = Room(
#                     name = room.name,
#                     description = room.description
#                 )

#                 self.db.add(db_room)
#             self.db.commit()
#             self.db.refresh(db_room)

#             return roomResponse.model_validate(db_room)

#         except Exception as error:
#             self.logger.error(f"Error adding room: {error}")
#             self.db.rollback()
#             return None
    
#     def get_all_rooms(self) -> list[roomResponse]:
#         try:
#             self.logger.info("Getting all rooms from the database")
#             rooms = self.db.query(Room).all()
#             return [roomResponse.model_validate(r) for r in rooms]
#         except Exception as error:
#             self.logger.error(f"Error getting rooms: {error}")
#             return []
