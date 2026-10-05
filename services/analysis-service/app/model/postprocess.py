import numpy as np

from app.api.schemas import ClassScore


def to_top_k(
    logits: np.ndarray,
    labels: list[str],
    top_k: int,
    output_activation: str = "softmax",
) -> tuple[str, float, list[ClassScore]]:
    output = np.asarray(logits, dtype=np.float64)
    if output.ndim == 2 and output.shape[0] != 1:
        raise ValueError("Model output must contain exactly one image prediction")
    if output.ndim not in (1, 2):
        raise ValueError("Model output must be a class-score vector")
    scores = output.reshape(-1)
    if scores.size != len(labels):
        raise ValueError(
            f"Model output has {scores.size} classes but labels.json has {len(labels)}"
        )
    if scores.size == 0 or not np.isfinite(scores).all():
        raise ValueError("Model output must contain finite class scores")

    if output_activation == "softmax":
        shifted = scores - np.max(scores)
        exponentials = np.exp(shifted)
        probabilities = exponentials / np.sum(exponentials)
    elif output_activation == "probabilities":
        if np.any(scores < 0.0) or np.any(scores > 1.0):
            raise ValueError("Probability output values must be in [0, 1]")
        if not np.isclose(np.sum(scores), 1.0, rtol=1e-3, atol=1e-3):
            raise ValueError("Probability output values must sum to 1")
        probabilities = scores
    else:
        raise ValueError("output_activation must be softmax or probabilities")

    selected = np.argsort(probabilities)[::-1][: min(top_k, len(labels))]
    top_classes = [
        ClassScore(label=labels[index], confidence=float(probabilities[index]))
        for index in selected
    ]
    best = top_classes[0]
    return best.label, best.confidence, top_classes
