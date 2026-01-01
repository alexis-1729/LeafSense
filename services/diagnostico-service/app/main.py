from fastapi import FastAPI
from .database import get_db, Base, engine
from .routes import predicts

Base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(predicts.router)