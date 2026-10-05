import base64
import binascii

from fastapi import APIRouter, HTTPException, Request, status
from starlette.concurrency import run_in_threadpool

from app.api.schemas import InferRequestV2, InferResponseV2
from app.core.config import get_settings
from app.model.predictor import Predictor

router = APIRouter(prefix="/v2/models/pest-cnn", tags=["inference"])


@router.post("/infer", response_model=InferResponseV2)
async def infer(payload: InferRequestV2, request: Request) -> InferResponseV2:
    settings = get_settings()
    encoded_image = payload.image
    max_encoded_size = 4 * ((settings.max_image_bytes + 2) // 3)
    if len(encoded_image) > max_encoded_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Encoded image exceeds the configured size limit",
        )

    try:
        image_bytes = base64.b64decode(encoded_image, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="image must contain valid standard base64",
        ) from exc

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="image must not be empty",
        )
    if len(image_bytes) > settings.max_image_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds the configured size limit",
        )

    predictor: Predictor | None = getattr(request.app.state, "predictor", None)
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded",
        )

    try:
        prediction = await run_in_threadpool(predictor.predict, image_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return InferResponseV2(**prediction)
