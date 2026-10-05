from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "live"}


@router.get("/health/ready")
def ready(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    with request.app.state.connection_factory(settings) as connection:
        connection.execute("SELECT 1")
    request.app.state.vector_store.ensure_collection()
    return {"status": "ready"}
