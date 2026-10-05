from fastapi import APIRouter, Request

from app.core.security import create_jwks

router = APIRouter(tags=["keys"])


@router.get("/jwks.json")
def jwks(request: Request) -> dict[str, list[dict[str, object]]]:
    return create_jwks(
        request.app.state.public_key,
        request.app.state.settings.jwt_key_id,
    )
