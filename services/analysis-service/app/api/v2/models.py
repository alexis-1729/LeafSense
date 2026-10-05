from fastapi import APIRouter

router = APIRouter(prefix="/v2", tags=["models"])


@router.get("/models")
def list_models() -> dict[str, list[dict[str, str]]]:
    return {"models": [{"name": "pest-cnn", "version": "2"}]}


@router.get("/models/pest-cnn")
def model_details() -> dict[str, str]:
    return {"name": "pest-cnn", "version": "2", "task": "image-classification"}
