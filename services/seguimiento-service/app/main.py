from fastapi import FastAPI
from .database import Base, engine
from app.routes import seguimiento_routes, fields_routes
Base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(seguimiento_routes.router)
app.include_router(fields_routes.router)