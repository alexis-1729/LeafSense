import io
import warnings

import numpy as np
from PIL import Image, UnidentifiedImageError

from app.core.config import Settings

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageValidationError(ValueError):
    pass


def preprocess_image(
    image_bytes: bytes,
    settings: Settings,
    layout: str = "NCHW",
) -> np.ndarray:
    if settings.input_width is None or settings.input_height is None:
        raise ValueError("Model input width and height must be resolved before preprocessing")
    Image.MAX_IMAGE_PIXELS = settings.max_image_pixels
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(image_bytes)) as source:
                if source.format not in ALLOWED_FORMATS:
                    raise ImageValidationError("Only JPEG, PNG, and WEBP images are supported")
                source.verify()
            with Image.open(io.BytesIO(image_bytes)) as source:
                if source.width * source.height > settings.max_image_pixels:
                    raise ImageValidationError("Image dimensions exceed the configured pixel limit")
                image = source.convert("RGB").resize(
                    (settings.input_width, settings.input_height),
                    Image.Resampling.BILINEAR,
                )
    except ImageValidationError:
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:
        raise ImageValidationError("Image is invalid or exceeds the configured pixel limit") from exc

    pixels = np.asarray(image, dtype=np.float32) / np.float32(255.0)
    mean = np.asarray(settings.image_mean, dtype=np.float32)
    std = np.asarray(settings.image_std, dtype=np.float32)
    normalized = (pixels - mean) / std
    if layout == "NCHW":
        normalized = np.transpose(normalized, (2, 0, 1))
    elif layout != "NHWC":
        raise ValueError(f"Unsupported ONNX input layout: {layout}")
    return normalized[np.newaxis, ...]
