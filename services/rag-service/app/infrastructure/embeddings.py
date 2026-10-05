from collections.abc import Sequence
import numpy as np
from sentence_transformers import SentenceTransformer


class LocalEmbedder:
    def __init__(self, model_name: str, cache_directory: str) -> None:
        self._model_name = model_name
        self._cache_directory = cache_directory
        self._model: SentenceTransformer | None = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(
                self._model_name,
                cache_folder=self._cache_directory,
                device="cpu",
            )
        return self._model

    def validate_dimension(self, expected_dimension: int) -> None:
        dimension = self._load_model().get_sentence_embedding_dimension()
        if dimension != expected_dimension:
            raise ValueError(
                f"Embedding model dimension {dimension} does not match configured "
                f"dimension {expected_dimension}"
            )

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._load_model()
        dimension = model.get_sentence_embedding_dimension()
        if dimension is None:
            raise ValueError("Embedding model does not declare its output dimension")
        vectors = model.encode(
            list(texts),
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        embeddings = np.asarray(vectors, dtype=np.float32)
        if embeddings.ndim != 2 or embeddings.shape != (len(texts), dimension):
            raise ValueError("Embedding model returned an unexpected output shape")
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embeddings = self.embed_documents([text])
        if len(embeddings) != 1:
            raise RuntimeError("Embedding model did not return a query embedding")
        return embeddings[0]
