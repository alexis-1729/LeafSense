from fastapi import FastAPI
from .database import  Base, engine
import firebase_admin
from firebase_admin import credentials, messaging
from app.routes import notification
import os
from dotenv import load_dotenv

load_dotenv()
Base.metadata.create_all(bind = engine)

app = FastAPI()


cred = credentials.Certificate(os.getenv('GOOGLE_APLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)

app.include_router(notification.router)