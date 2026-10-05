from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import diagnosis
from app.core.security import get_current_claims
from app.infrastructure.analysis_client import AnalysisPrediction, AnalysisPredictionScore
from app.infrastructure.llm.openai_compatible import LLMNotConfiguredError
from app.schemas.diagnosis import DiagnosisContent

IMAGE = b"\xff\xd8\xffjpeg"
USER_ID = uuid4()
DOCUMENT_ID = uuid4()


class FakeRepository:
    calls: list[tuple[object, ...]] = []

    def __init__(self, _connection: object) -> None:
        self.connection = _connection

    def create(self, *values: object) -> object:
        self.calls.append(values)
        return uuid4()


class FakeAnalysis:
    def __init__(self, prediction: AnalysisPrediction) -> None:
        self.prediction = prediction
        self.calls = 0

    async def infer(self, _image: bytes) -> AnalysisPrediction:
        self.image = _image
        self.calls += 1
        return self.prediction


class FakeEmbedder:
    def __init__(self) -> None:
        self.calls = 0

    def embed_query(self, _text: str) -> list[float]:
        self.text = _text
        self.calls += 1
        return [0.1, 0.2]


class FakeVectorStore:
    def __init__(self, results: list[dict[str, object]]) -> None:
        self.results = results
        self.calls = 0

    def search(
        self,
        _vector: list[float],
        _pest_label: str,
        _limit: int,
    ) -> list[dict[str, object]]:
        self.search_parameters = (_vector, _pest_label, _limit)
        self.calls += 1
        return self.results


class FakeLLM:
    def __init__(
        self,
        content: DiagnosisContent | None = None,
        error: Exception | None = None,
    ) -> None:
        self.content = content
        self.error = error
        self.calls = 0

    async def generate(self, *_prompts: str) -> DiagnosisContent:
        self.prompts = _prompts
        self.calls += 1
        if self.error:
            raise self.error
        if self.content is None:
            raise AssertionError("Fake LLM has no diagnosis content")
        return self.content


def _source() -> dict[str, object]:
    return {
        "doc_id": str(DOCUMENT_ID),
        "source": "guía agrícola",
        "crop": "tomate",
        "language": "es",
        "text": "La plaga causa manchas en las hojas.",
        "score": 0.87,
    }


def _client(
    monkeypatch: pytest.MonkeyPatch,
    confidence: float,
    sources: list[dict[str, object]] | None = None,
    llm: FakeLLM | None = None,
) -> tuple[TestClient, FakeAnalysis, FakeEmbedder, FakeVectorStore, FakeLLM]:
    FakeRepository.calls = []
    prediction = AnalysisPrediction(
        label="mosca_blanca",
        confidence=confidence,
        top_k=[
            AnalysisPredictionScore(label="mosca_blanca", confidence=confidence),
            AnalysisPredictionScore(label="pulgon", confidence=1 - confidence),
        ],
    )
    analysis_client = FakeAnalysis(prediction)
    embedder = FakeEmbedder()
    vector_store = FakeVectorStore(sources or [])
    llm_client = llm or FakeLLM(
        DiagnosisContent(
            summary="Se observan indicios compatibles con mosca blanca.",
            severity="medium",
            recommendations=["Verificar el envés de las hojas."],
            limitations=["La imagen no permite confirmar todos los síntomas."],
        )
    )

    app = FastAPI()
    app.state.settings = SimpleNamespace(
        max_image_bytes=64,
        diagnosis_confidence_threshold=0.60,
    )
    app.state.analysis_client = analysis_client
    app.state.embedder = embedder
    app.state.vector_store = vector_store
    app.state.llm = llm_client
    app.dependency_overrides[get_current_claims] = lambda: {"sub": str(USER_ID), "role": "user"}
    app.dependency_overrides[diagnosis.get_connection] = lambda: object()
    app.include_router(diagnosis.router)
    monkeypatch.setattr(diagnosis, "DiagnosisRepository", FakeRepository)
    return TestClient(app), analysis_client, embedder, vector_store, llm_client


def test_low_confidence_returns_non_conclusive_without_retrieval_or_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, analysis_client, embedder, vector_store, llm = _client(monkeypatch, 0.59)

    response = client.post(
        "/rag/diagnose",
        files={"image": ("leaf.jpg", IMAGE, "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["conclusive"] is False
    assert response.json()["diagnosis"] is None
    assert response.json()["top_k"][0]["label"] == "mosca_blanca"
    assert analysis_client.calls == 1
    assert embedder.calls == vector_store.calls == llm.calls == 0
    assert len(FakeRepository.calls) == 1


@pytest.mark.parametrize("confidence", [0.60, 0.82])
def test_conclusive_path_retrieves_sources_calls_llm_and_persists(
    monkeypatch: pytest.MonkeyPatch,
    confidence: float,
) -> None:
    client, _, embedder, vector_store, llm = _client(
        monkeypatch,
        confidence,
        [_source()],
    )

    response = client.post(
        "/rag/diagnose",
        files={"image": ("leaf.jpg", IMAGE, "image/jpeg")},
        data={"crop": "tomate", "language": "es"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["conclusive"] is True
    assert body["diagnosis"]["severity"] == "medium"
    assert body["sources"][0]["document_id"] == str(DOCUMENT_ID)
    assert embedder.calls == vector_store.calls == llm.calls == 1
    assert len(FakeRepository.calls) == 1
    assert FakeRepository.calls[0][0] == USER_ID
    assert FakeRepository.calls[0][5] is True


def test_no_matching_sources_returns_non_conclusive_without_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, embedder, vector_store, llm = _client(monkeypatch, 0.9)

    response = client.post(
        "/rag/diagnose",
        files={"image": ("leaf.jpg", IMAGE, "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["conclusive"] is False
    assert "no hay documentos" in response.json()["message"]
    assert embedder.calls == vector_store.calls == 1
    assert llm.calls == 0
    assert len(FakeRepository.calls) == 1


def test_missing_llm_key_returns_service_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    llm = FakeLLM(error=LLMNotConfiguredError())
    client, _, _, _, _ = _client(monkeypatch, 0.9, [_source()], llm)

    response = client.post(
        "/rag/diagnose",
        files={"image": ("leaf.jpg", IMAGE, "image/jpeg")},
    )

    assert response.status_code == 503
    assert "LLM_API_KEY" in response.json()["detail"]
    assert FakeRepository.calls == []


@pytest.mark.parametrize(
    ("image", "expected_status"),
    [
        (b"not-an-image", 415),
        (b"\xff\xd8\xff" + (b"x" * 64), 413),
    ],
)
def test_rejects_invalid_or_oversized_images(
    monkeypatch: pytest.MonkeyPatch,
    image: bytes,
    expected_status: int,
) -> None:
    client, analysis_client, _, _, _ = _client(monkeypatch, 0.9)

    response = client.post(
        "/rag/diagnose",
        files={"image": ("leaf.jpg", image, "image/jpeg")},
    )

    assert response.status_code == expected_status
    assert analysis_client.calls == 0
