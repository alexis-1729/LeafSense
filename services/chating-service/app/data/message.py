from sqlalchemy.orm import Session
from app.schemas.message import messageCreate, messageResponse
from app.models import Message
from sqlalchemy import or_, and_
import logging
from uuid import UUID

class MessageData:

    def __init__(self, db: Session)-> None:
        self.db = db
        self.logger = logging.getLogger("MessagingData")
    
    def add_message(self, message: messageCreate):
        try:
            self.logger.info("Adding message to the database")
            db_message = Message(
                sender_id = message.sender_id,
                reciver_id = message.reciver_id,
                message = message.message
            )

            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            
            new_message = messageResponse(
                id_message = db_message.id_message,
                sender_id = db_message.sender_id,
                reciver_id = db_message.reciver_id,
                message = db_message.message,
                created_at = db_message.created_at
            )

            print("se agrego el dato")

            return new_message
        except Exception as error:
            self.logger.error(f"Error adding message: {error}")
            self.db.rollback()
            return None
        
    def get_messages(self, user_id: UUID, user_id2: UUID)-> list[messageResponse] | None:
        try:
            self.logger.info(f"Getting message of {user_id} ans {user_id2}")

            messages = (
                self.db.query(Message)
                .filter(
                    or_(
                        and_(Message.sender_id == user_id, Message.reciver_id == user_id2),
                       and_(Message.sender_id == user_id2, Message.reciver_id == user_id),
                    )
                )
                .order_by(Message.created_at.asc())
                .all()
            )
            if not messages :
                self.logger.info("no hay naaa")

            return [messageResponse(
                    id_message = m.id_message,
                    sender_id = m.sender_id,
                    reciver_id = m.reciver_id,
                    message = m.message,
                    created_at = m.created_at
                   ) 
                    for m in messages]
        except Exception as error:
            self.logger.info(f"Error getting message: {error}")
            return None

    def get_message(self, user_id: UUID)-> list[messageResponse] | None:
        try:
            self.logger.info(f"Getting message of {user_id}")

            messages = (
                self.db.query(Message)
                .filter(Message.sender_id == user_id)
                .order_by(Message.created_at.asc())
                .all()
            )
            if not messages :
                self.logger.info("no hay naaa")

            return [messageResponse.model_validate(m) for m in messages]
        except Exception as error:
            self.logger.info(f"Error getting message: {error}")
            return None
    
# user 1: 550e8400-e29b-41d4-a716-446655440000
# user 2: 123e4567-e89b-12d3-a456-426614174000