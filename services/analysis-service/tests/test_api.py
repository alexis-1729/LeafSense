import base64

from fastapi.testclient import TestClient

from app.main import app


class FakePredictor:
    def predict(self, image_bytes: bytes) -> dict[str, object]:
        assert image_bytes == b"sample-image"
        return {
            "label": "aphid",
            "confidence": 0.8,
            "top_k": [{"label": "aphid", "confidence": 0.8}],
        }


def test_infer_v2_decodes_image_and_returns_prediction(monkeypatch) -> None:
    monkeypatch.setattr("app.main.load_predictor", lambda settings: FakePredictor())

    with TestClient(app) as client:
        response = client.post(
            "/v2/models/pest-cnn/infer",
            json={"image": base64.b64encode(b"sample-image").decode("ascii")},
        )

    assert response.status_code == 200
    assert response.json() == {
        "label": "aphid",
        "confidence": 0.8,
        "top_k": [{"label": "aphid", "confidence": 0.8}],
    }


def test_infer_v2_rejects_invalid_base64(monkeypatch) -> None:
    monkeypatch.setattr("app.main.load_predictor", lambda settings: FakePredictor())

    with TestClient(app) as client:
        response = client.post(
            "/v2/models/pest-cnn/infer",
            json={"image": "not-base64"},
        )

    assert response.status_code == 422
