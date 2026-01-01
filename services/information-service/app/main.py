from fastapi import FastAPI
from app.database import get_db, Base, engine
from app.routes import recomendation, pests,admin_treatment, admin_recomendation  

Base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(pests.router)
app.include_router(admin_recomendation.router)
app.include_router(admin_treatment.router)
app.include_router(recomendation.router)

@app.on_event("startup")
async def print_routes():
    print("🚀 Rutas cargadas:")
    for route in app.router.routes:
        print(f"{route.path} -> {route.name}")