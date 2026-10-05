import base64

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class AnalysisPredictionScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class AnalysisPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    top_k: list[AnalysisPredictionScore]


class AnalysisServiceUnavailable(Exception):
    pass


class AnalysisServiceInvalidResponse(Exception):
    pass


class AnalysisInputRejected(Exception):
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"Analysis service rejected the image ({status_code})")


class AnalysisServiceClient:
    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client

    async def infer(self, image: bytes) -> AnalysisPrediction:
        payload = {"image": base64.b64encode(image).decode("ascii")}
        try:
            response = await self._client.post(
                f"{self._base_url}/v2/models/pest-cnn/infer",
                json=payload,
            )
        except httpx.HTTPError as exc:
            raise AnalysisServiceUnavailable(
                "Analysis service could not be reached"
            ) from exc

        if response.status_code in (413, 422):
            raise AnalysisInputRejected(response.status_code)
        if not response.is_success:
            raise AnalysisServiceUnavailable(
                f"Analysis service returned HTTP {response.status_code}"
            )
        try:
            body = response.json()
        except ValueError as exc:
            raise AnalysisServiceInvalidResponse(
                "Analysis service returned invalid JSON"
            ) from exc
        try:
            return AnalysisPrediction.model_validate(body)
        except ValidationError as exc:
            raise AnalysisServiceInvalidResponse(
                "Analysis service returned an invalid prediction"
            ) from exc
