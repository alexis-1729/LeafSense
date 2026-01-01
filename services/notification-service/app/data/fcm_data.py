import firebase_admin
from firebase_admin import credentials, messaging
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import FCMToken
from app.schemas.token import tokenCreate, notificationResponse, tokenResponse
import logging

class FCMData:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("FCMService")

    def set_token(self, data: tokenCreate):
        try:
            exist = self.get_token(data.user_id)
            if exist:
                if exist.token != data.token:
                    return self.update_token(exist, data)
                else:
                    return exist
            else:
                new_token = FCMToken(**data.dict())
                self.db.add(new_token)
                self.db.commit()
                self.db.refresh(new_token)
                return new_token
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error en la creacion de nuevo token {e}")
            return None
    
    def get_token(self, user_id: UUID):
        try:
            token = self.db.query(FCMToken).filter(FCMToken.user_id == user_id).first()
            return token
        except Exception as e:
            self.logger.error(f"Errror in DB Token: {e}")
            

    
    def update_token(self, user_token, token: tokenCreate):
        try:
            if user_token:
                user_token.token = token.token
                self.db.commit()
                return user_token
        except Exception as e:
            self.logger.error(f"Error with update token: {e}")
            return None
    
    def delete_token(self, token: str):
        try:
            d_token = self.db.query(FCMToken).query(FCMToken.token == token).first()
            self.db.delete(d_token)
            self.db.commit()
        except Exception as e:
            self.rollback()
            self.logger.error(f"Error with the elimination {e}")


        
