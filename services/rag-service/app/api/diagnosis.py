from typing import Annotated
from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.api.deps import CurrentClaims, get_connection
from app.infrastructure.analysis_client import (
    AnalysisInputRejected,
    AnalysisServiceInvalidResponse,
    AnalysisServiceUnavailable,
)
from app.infrastructure.persistence.diagnosis_repo import DiagnosisRepository
from app.infrastructure.llm.openai_compatible import (
    LLMNotConfiguredError,
    LLMResponseError,
    LLMServiceError,
)
from app.schemas.diagnosis import DiagnosisResponse, DiagnosisSource
from app.services.prompt_builder import build_diagnosis_prompts
from app.services.query_builder import build_diagnosis_query

router = APIRouter(prefix="/rag", tags=["diagnosis"])
TOP_K = 5


def _supported_image(image: bytes) -> bool:
    return (
        image.startswith(b"\xff\xd8\xff")
        or image.startswith(b"\x89PNG\r\n\x1a\n")
        or (image.startswith(b"RIFF") and image[8:12] == b"WEBP")
    )


def _to_source_response(source: dict[str, object]) -> DiagnosisSource:
    document_id = source["doc_id"]
    score = source["score"]
    if not isinstance(document_id, str) or not isinstance(score, (int, float)):
        raise ValueError("Retrieved source has invalid identity or score")
    text = source["text"]
    if not isinstance(text, str):
        raise ValueError("Retrieved source has invalid text")
    return DiagnosisSource(
        document_id=UUID(document_id),
        source=str(source["source"]),
        crop=str(source["crop"]),
        language=str(source["language"]),
        score=float(score),
        excerpt=text,
    )


@router.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose(
    request: Request,
    claims: CurrentClaims,
    image: Annotated[UploadFile, File()],
    connection: Annotated[psycopg.Connection, Depends(get_connection)],
    crop: Annotated[str | None, Form(max_length=100)] = None,
    language: Annotated[str, Form(min_length=2, max_length=12)] = "es",
) -> DiagnosisResponse:
    settings = request.app.state.settings
    image_bytes = await image.read(settings.max_image_bytes + 1)
    if len(image_bytes) > settings.max_image_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds the {settings.max_image_bytes}-byte limit",
        )
    if not image_bytes or not _supported_image(image_bytes):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Image must be a valid JPEG, PNG, or WEBP file",
        )

    crop_value = crop.strip() if crop and crop.strip() else None
    language_value = language.strip().lower()
    try:
        prediction = await request.app.state.analysis_client.infer(image_bytes)
    except AnalysisInputRejected as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail="Analysis service rejected the image",
        ) from exc
    except AnalysisServiceUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pest analysis service is unavailable",
        ) from exc
    except AnalysisServiceInvalidResponse as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Pest analysis service returned an invalid prediction",
        ) from exc

    top_k = [score.model_dump() for score in prediction.top_k]
    prediction_values = {
        "pest_label": prediction.label,
        "confidence": prediction.confidence,
        "top_k": top_k,
    }
    repository = DiagnosisRepository(connection)
    user_id = UUID(claims["sub"])

    if prediction.confidence < settings.diagnosis_confidence_threshold:
        diagnosis_id = await run_in_threadpool(
            repository.create,
            user_id,
            crop_value,
            prediction.label,
            prediction.confidence,
            top_k,
            False,
            None,
            [],
        )
        return DiagnosisResponse(
            id=diagnosis_id,
            **prediction_values,
            conclusive=False,
            diagnosis=None,
            message="No concluyente: la confianza de la clasificación es baja.",
            sources=[],
        )

    query = build_diagnosis_query(prediction.label, crop_value)
    query_vector = await run_in_threadpool(request.app.state.embedder.embed_query, query)
    retrieved = await run_in_threadpool(
        request.app.state.vector_store.search,
        query_vector,
        prediction.label,
        TOP_K,
    )
    sources = [_to_source_response(source) for source in retrieved]

    if not sources:
        message = "No concluyente: no hay documentos indexados para esta plaga."
        diagnosis_id = await run_in_threadpool(
            repository.create,
            user_id,
            crop_value,
            prediction.label,
            prediction.confidence,
            top_k,
            False,
            None,
            [],
        )
        return DiagnosisResponse(
            id=diagnosis_id,
            **prediction_values,
            conclusive=False,
            diagnosis=None,
            message=message,
            sources=[],
        )

    prompts = build_diagnosis_prompts(
        prediction.label,
        prediction.confidence,
        crop_value,
        language_value,
        retrieved,
    )
    try:
        generated = await request.app.state.llm.generate(*prompts)
    except LLMNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM_API_KEY is not configured",
        ) from exc
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM provider is unavailable or rejected the request",
        ) from exc
    except LLMResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM provider returned an invalid structured diagnosis",
        ) from exc

    diagnosis_data = generated.model_dump()
    source_data = [source.model_dump(mode="json") for source in sources]
    diagnosis_id = await run_in_threadpool(
        repository.create,
        user_id,
        crop_value,
        prediction.label,
        prediction.confidence,
        top_k,
        True,
        diagnosis_data,
        source_data,
    )
    return DiagnosisResponse(
        id=diagnosis_id,
        **prediction_values,
        conclusive=True,
        diagnosis=generated,
        message=None,
        sources=sources,
    )
