import httpx
from pydantic import ValidationError

from app.schemas.diagnosis import DiagnosisContent


class LLMNotConfiguredError(Exception):
    pass


class LLMServiceError(Exception):
    pass


class LLMResponseError(Exception):
    pass


class OpenAICompatibleLLM:
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._client = client

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> DiagnosisContent:
        if not self._api_key:
            raise LLMNotConfiguredError("LLM_API_KEY is not configured")
        try:
            response = await self._client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "temperature": 0.2,
                    "max_tokens": 700,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
        except httpx.HTTPError as exc:
            raise LLMServiceError("LLM provider could not be reached") from exc

        if response.status_code == 429 or response.status_code >= 500:
            raise LLMServiceError(
                f"LLM provider returned HTTP {response.status_code}"
            )
        if not response.is_success:
            raise LLMServiceError(
                f"LLM provider rejected the request ({response.status_code})"
            )
        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise TypeError("LLM response content must be a string")
            return DiagnosisContent.model_validate_json(content)
        except (KeyError, IndexError, TypeError, ValueError, ValidationError) as exc:
            raise LLMResponseError(
                "LLM provider returned an invalid structured diagnosis"
            ) from exc
