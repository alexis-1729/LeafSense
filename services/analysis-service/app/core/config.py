import os
from dataclasses import dataclass
from functools import lru_cache


def _parse_float_tuple(name: str, default: tuple[float, ...]) -> tuple[float, ...]:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        values = tuple(float(item.strip()) for item in raw_value.split(","))
    except ValueError as exc:
        raise ValueError(f"{name} must be a comma-separated list of numbers") from exc
    if len(values) != 3:
        raise ValueError(f"{name} must contain exactly three values")
    return values


def _parse_optional_positive_int(name: str) -> int | None:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return None
    value = int(raw_value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


@dataclass(frozen=True)
class Settings:
    model_path: str
    labels_path: str
    input_width: int | None
    input_height: int | None
    image_mean: tuple[float, float, float]
    image_std: tuple[float, float, float]
    max_image_bytes: int
    max_image_pixels: int
    top_k: int
    output_activation: str = "softmax"


@lru_cache
def get_settings() -> Settings:
    settings = Settings(
        model_path=os.getenv("MODEL_PATH", "/models/pest-cnn.onnx"),
        labels_path=os.getenv("LABELS_PATH", "/models/labels.json"),
        input_width=_parse_optional_positive_int("MODEL_INPUT_WIDTH"),
        input_height=_parse_optional_positive_int("MODEL_INPUT_HEIGHT"),
        image_mean=_parse_float_tuple(
            "MODEL_IMAGE_MEAN",
            (0.0, 0.0, 0.0),
        ),
        image_std=_parse_float_tuple(
            "MODEL_IMAGE_STD",
            (1.0, 1.0, 1.0),
        ),
        max_image_bytes=int(os.getenv("MAX_IMAGE_BYTES", str(10 * 1024 * 1024))),
        max_image_pixels=int(os.getenv("MAX_IMAGE_PIXELS", str(40_000_000))),
        top_k=int(os.getenv("MODEL_TOP_K", "3")),
        output_activation=os.getenv("MODEL_OUTPUT_ACTIVATION", "softmax").lower(),
    )
    if any(value <= 0 for value in settings.image_std):
        raise ValueError("MODEL_IMAGE_STD values must be positive")
    if settings.max_image_bytes <= 0 or settings.max_image_pixels <= 0:
        raise ValueError("Image size limits must be positive")
    if settings.top_k <= 0:
        raise ValueError("MODEL_TOP_K must be positive")
    if settings.output_activation not in {"softmax", "probabilities"}:
        raise ValueError("MODEL_OUTPUT_ACTIVATION must be softmax or probabilities")
    return settings
