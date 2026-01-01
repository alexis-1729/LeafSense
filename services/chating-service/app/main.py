from fastapi import FastAPI
from app.database import Base, engine
import firebase_admin
from app.routes.server import router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind = engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- para pruebas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)