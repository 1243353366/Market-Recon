from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    @property
    def dimension(self) -> int: ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class SentenceTransformerEmbedder:
    """Lazy-loaded multilingual/general embedding adapter using sentence-transformers."""

    def __init__(self, model_name: str = "BAAI/bge-m3") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover - optional dependency guard
            raise RuntimeError("Install the 'rag' extra to use embedding models") from exc
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self._dimension = int(self._model.get_sentence_embedding_dimension())

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        # BGE and Jina models accept natural-language queries; E5 uses a query prefix.
        query = f"query: {text}" if "e5" in self.model_name.lower() else text
        return self._model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0].tolist()
