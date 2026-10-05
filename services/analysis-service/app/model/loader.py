import json
import logging
from pathlib import Path

import onnxruntime as ort

logger = logging.getLogger(__name__)


def load_labels(labels_path: str) -> list[str]:
    path = Path(labels_path)
    if not path.is_file():
        raise FileNotFoundError(f"Labels file does not exist: {path}")
    try:
        contents = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read labels file: {path}") from exc

    labels = contents.get("labels") if isinstance(contents, dict) else contents
    if (
        not isinstance(labels, list)
        or not labels
        or any(not isinstance(label, str) or not label.strip() for label in labels)
    ):
        raise ValueError("labels.json must contain a non-empty list of label strings")
    if len(set(labels)) != len(labels):
        raise ValueError("labels.json must not contain duplicate labels")
    return labels


def load_session(model_path: str) -> ort.InferenceSession:
    path = Path(model_path)
    if path.suffix.lower() != ".onnx":
        raise ValueError("MODEL_PATH must reference an ONNX model")
    if not path.is_file():
        raise FileNotFoundError(f"ONNX model does not exist: {path}")

    session = ort.InferenceSession(
        str(path),
        providers=["CPUExecutionProvider"],
    )
    if len(session.get_inputs()) != 1 or len(session.get_outputs()) != 1:
        raise ValueError("The ONNX model must have exactly one input and one output")

    input_shape = session.get_inputs()[0].shape
    if len(input_shape) != 4:
        raise ValueError("The ONNX model input must have rank 4 (NCHW or NHWC)")
    if input_shape[1] != 3 and input_shape[3] != 3:
        raise ValueError("The ONNX model must accept three-channel RGB input")
    if input_shape[1] == 3 and input_shape[3] == 3:
        raise ValueError("Cannot determine ONNX input layout unambiguously")
    if session.get_inputs()[0].type != "tensor(float)":
        raise ValueError("The ONNX model input must use float32 tensors")

    logger.info("Loaded ONNX classifier from %s", path.name)
    return session
