import numpy as np
import pytest

from app.model.postprocess import to_top_k


def test_to_top_k_returns_softmax_in_descending_order() -> None:
    label, confidence, scores = to_top_k(
        np.array([[0.0, 2.0, 1.0]]),
        ["aphid", "rust", "mildew"],
        2,
    )

    assert label == "rust"
    assert confidence == pytest.approx(0.66524096)
    assert [score.label for score in scores] == ["rust", "mildew"]
    assert sum(score.confidence for score in scores) < 1.0


def test_to_top_k_rejects_label_count_mismatch() -> None:
    with pytest.raises(ValueError, match="labels.json"):
        to_top_k(np.array([1.0, 2.0]), ["aphid"], 3)


def test_to_top_k_rejects_non_finite_scores() -> None:
    with pytest.raises(ValueError, match="finite"):
        to_top_k(np.array([1.0, np.nan]), ["aphid", "rust"], 2)


def test_to_top_k_rejects_multiple_images() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        to_top_k(np.array([[1.0, 2.0], [2.0, 1.0]]), ["aphid", "rust"], 2)


def test_to_top_k_preserves_softmax_probabilities() -> None:
    label, confidence, scores = to_top_k(
        np.array([[0.1, 0.7, 0.2]]),
        ["aphid", "rust", "mildew"],
        2,
        output_activation="probabilities",
    )

    assert label == "rust"
    assert confidence == pytest.approx(0.7)
    assert [score.confidence for score in scores] == pytest.approx([0.7, 0.2])


def test_to_top_k_rejects_invalid_probability_output() -> None:
    with pytest.raises(ValueError, match="sum to 1"):
        to_top_k(
            np.array([[0.1, 0.7, 0.1]]),
            ["aphid", "rust", "mildew"],
            2,
            output_activation="probabilities",
        )
