from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.data.seguimiento_data import SeguimientoData
from app.schemas.seguimiento import seguimientoCreate
from app.data.semanaSeguimiento_data import SemanaData
from app.schemas.semanaSeguimiento import semanaSeguimientoCreate
from app.data.diagnosticoSeguimiento_data import DiagnosticoData
from app.schemas.diagnosticoSemana import diagnosticoSemanalCreate
from app.data.aplication_data import AplicationData
from app.schemas.aplication import aplicationCreate


from uuid import UUID
import logging
router = APIRouter(
    prefix = "/seguimiento",
    tags = ["Seguimiento"]
)

api_logger = logging.getLogger("API")


@router.post("/iniciar/seguimiento/")
def init_diagnostic(data: seguimientoCreate, db: Session = Depends(get_db)):
    try:
        seguimiento_data = SeguimientoData(db)
        new = seguimiento_data.add_seguimiento(data)
        if new:
            semana_data = SemanaData(db)
            dato = semanaSeguimientoCreate(
                id_seguimiento = new.seguimiento_id
            )
            #creamos semana
            sem = semana_data.add_semana(dato)
            if sem:
                return {"seguimiento": new, "semana": sem.semana_id}
            else:
                raise HTTPException(status_code = 500, detail="Algo salio mal")
        else:
            raise HTTPException(status_code = 404, detail= "Error en la creacion")
    except Exception as e:
        raise HTTPException(status_code = 500, detail ="Algo ocurrio mal: {e}")


@router.post("/iniciar/aplicacion")
async def create_aplication(data: aplicationCreate, data2: diagnosticoSemanalCreate, db: Session = Depends(get_db)):
    try:
        aplication_data = AplicationData(db)
        new = aplication_data.add_aplication(data)
        if not new:
            return None
        new2 = await save_diagnostic(data2, db)
        if new2:
            return {"aplicacion": new, "diagnostico": new2}
    except Exception as e: 
        raise HTTPException(status_code = 500, detail = "Error en el servidor: {e}")

# def completeRegisterDiagnostic(data: diagnosticoSemanalCreate, data2: recomendacionSemanalCreate, db: Session = (Depends(get_db))):
#     try:
#         new_diagnostic = save_diagnostic(data, db)
#         if not new_diagnostic:
#             return None

#         new_recomendacion =save_recomendacion(data2, db)
#         if not new_recomendacion:
#             return None
#         return {"response": "success", "detail":"Operacion correctamente finalizadas"}
#     except Exception as e:
#         raise HTTPException(status_code = 500, detail = "No se pudo completar el registro")


async def save_diagnostic(data: diagnosticoSemanalCreate,db: Session):
    try:
        diagnostic_data = DiagnosticoData(db)
        new = diagnostic_data.add_diagnostico(data)
        if new:
            return new
        else: 
            return None
        
    except Exception as e:
        raise HTTPException(status_code = 500, detail = "No se pudo guardar el diagnostico")

# def save_recomendacion(data: recomendacionSemanalCreate, db: Session):
#     try:
#         recomendacion_data = RecomendacionData(db)
#         new =recomendacion_data.add_recomendacion(data)
#         if new:
#             return new
#         else: None
#     except Exception as e:
#         raise HTTPException(status_code = 500, detail = "No se pudo guardar la recomendacion")