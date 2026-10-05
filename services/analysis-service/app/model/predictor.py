import logging
from dataclasses import replace

import numpy as np
import onnxruntime as ort

from app.core.config import Settings
from app.model.loader import load_labels, load_session
from app.model.preprocess import ImageValidationError, preprocess_image
from app.model.postprocess import to_top_k

logger = logging.getLogger(__name__)


class Predictor:
    def __init__(
        self,
        session: ort.InferenceSession,
        labels: list[str],
        settings: Settings,
    ) -> None:
        self._session = session
        self._input_name = session.get_inputs()[0].name
        self._labels = labels
        self._settings = settings
        self._layout = "NCHW" if session.get_inputs()[0].shape[1] == 3 else "NHWC"

    @classmethod
    def load(cls, settings: Settings) -> "Predictor":
        labels = load_labels(settings.labels_path)
        session = load_session(settings.model_path)
        input_shape = session.get_inputs()[0].shape
        layout = "NCHW" if input_shape[1] == 3 else "NHWC"
        if layout == "NCHW":
            height_dimension, width_dimension = input_shape[2], input_shape[3]
        else:
            height_dimension, width_dimension = input_shape[1], input_shape[2]

        model_height = height_dimension if isinstance(height_dimension, int) else None
        model_width = width_dimension if isinstance(width_dimension, int) else None
        if (
            settings.input_height is not None
            and model_height is not None
            and settings.input_height != model_height
        ):
            raise ValueError("Configured input height does not match the ONNX model")
        if (
            settings.input_width is not None
            and model_width is not None
            and settings.input_width != model_width
        ):
            raise ValueError("Configured input width does not match the ONNX model")
        resolved_height = model_height or settings.input_height or 224
        resolved_width = model_width or settings.input_width or 224
        output_shape = session.get_outputs()[0].shape
        if len(output_shape) != 2:
            raise ValueError("The ONNX model output must have rank 2 (batch, classes)")
        if output_shape[-1] not in (None, len(labels)):
            raise ValueError("ONNX output class count does not match labels.json")
        settings = replace(
            settings,
            input_width=resolved_width,
            input_height=resolved_height,
        )
        logger.info("Loaded classifier with %d labels", len(labels))
        return cls(session, labels, settings)

    def predict(self, image_bytes: bytes) -> dict[str, object]:
        try:
            input_tensor = preprocess_image(
                image_bytes,
                self._settings,
                self._layout,
            )
        except ImageValidationError as exc:
            raise ValueError(str(exc)) from exc

        logits = self._session.run(None, {self._input_name: input_tensor})[0]
        label, confidence, top_k = to_top_k(
            np.asarray(logits),
            self._labels,
            self._settings.top_k,
            self._settings.output_activation,
        )
        return {
            "label": label,
            "confidence": confidence,
            "top_k": [item.model_dump() for item in top_k],
        }


def load_predictor(settings: Settings) -> Predictor:
    return Predictor.load(settings)
