import io

import numpy as np
import pytest
from PIL import Image

from app.core.config import Settings
from app.model.preprocess import ImageValidationError, preprocess_image


@pytest.fixture
def settings() -> Settings:
    return Settings(
        model_path="model.onnx",
        labels_path="labels.json",
        input_width=2,
        input_height=2,
        image_mean=(0.0, 0.0, 0.0),
        image_std=(1.0, 1.0, 1.0),
        max_image_bytes=1024,
        max_image_pixels=100,
        top_k=3,
    )


def test_preprocess_returns_normalized_nchw_rgb(settings: Settings) -> None:
    image = Image.new("RGB", (2, 2), (255, 0, 0))
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")

    result = preprocess_image(image_bytes.getvalue(), settings)

    assert result.shape == (1, 3, 2, 2)
    np.testing.assert_allclose(result[0, :, 0, 0], [1.0, 0.0, 0.0])


def test_preprocess_returns_nhwc_when_model_expects_it(settings: Settings) -> None:
    image = Image.new("RGB", (2, 2), (255, 0, 0))
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")

    result = preprocess_image(image_bytes.getvalue(), settings, layout="NHWC")

    assert result.shape == (1, 2, 2, 3)
    np.testing.assert_allclose(result[0, 0, 0], [1.0, 0.0, 0.0])


def test_preprocess_rejects_non_image_bytes(settings: Settings) -> None:
    with pytest.raises(ImageValidationError, match="invalid"):
        preprocess_image(b"not an image", settings)


def test_preprocess_rejects_unsupported_format(settings: Settings) -> None:
    image = Image.new("RGB", (1, 1))
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="BMP")

    with pytest.raises(ImageValidationError, match="Only JPEG"):
        preprocess_image(image_bytes.getvalue(), settings)
