from __future__ import annotations

import pickle
import threading
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover - depends on environment
    faiss = None

try:
    from config import settings
except ImportError:  # pragma: no cover - allows importing from repo root
    from backend.config import settings

_INDEX_EXT = ".faiss"
_META_EXT = ".pkl"
_MODEL_LOCK = threading.Lock()
_RETRIEVER_LOCK = threading.Lock()
_EMBED_MODEL: SentenceTransformer | None = None
_RETRIEVER: "LocalDocsRetriever | None" = None


def _require_faiss() -> Any:
    if faiss is None:  # pragma: no cover - depends on environment
        raise ImportError(
            "faiss-cpu is required for local retrieval. Install dependencies from requirements.txt first."
        )
    return faiss


def _artifact_paths(base_path: str | Path) -> tuple[Path, Path]:
    base = Path(base_path)
    if not base.is_absolute():
        base = Path(settings.ROOT_DIR) / base
    return base.with_suffix(_INDEX_EXT), base.with_suffix(_META_EXT)


def _normalize_source(source: str) -> str:
    normalized = (source or "").strip().lower()
    if normalized in {"azure", "gcp", "compliance"}:
        return normalized
    raise ValueError(f"Unsupported retrieval source '{source}'. Expected one of: compliance, azure, gcp.")


def _missing_index_message(source: str, base_path: str | Path) -> str:
    index_path, metadata_path = _artifact_paths(base_path)
    return (
        f"The {source} FAISS index is missing ({index_path.name} / {metadata_path.name}). "
        f"Run 'python scripts/build_index.py' from the project root first."
    )


def _resolve_index_bases() -> dict[str, str]:
    return {
        "compliance": settings.COMPLIANCE_INDEX_PATH,
        "azure": settings.AZURE_INDEX_PATH,
        "gcp": settings.GCP_INDEX_PATH,
    }


def get_embedding_model() -> SentenceTransformer:
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        with _MODEL_LOCK:
            if _EMBED_MODEL is None:
                try:
                    _EMBED_MODEL = SentenceTransformer(settings.EMBEDDING_MODEL, local_files_only=True)
                except Exception:
                    _EMBED_MODEL = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _EMBED_MODEL


class LocalDocsRetriever:
    def __init__(self):
        self._faiss = _require_faiss()
        self._model = get_embedding_model()
        self._indices: dict[str, Any] = {}
        self._metadata: dict[str, list[dict[str, Any]]] = {}
        self._load_indexes()

    def _load_indexes(self) -> None:
        for source, base_path in _resolve_index_bases().items():
            index_path, metadata_path = _artifact_paths(base_path)
            if not index_path.exists() or not metadata_path.exists():
                raise FileNotFoundError(_missing_index_message(source, base_path))
            self._indices[source] = self._faiss.read_index(str(index_path))
            with metadata_path.open("rb") as handle:
                self._metadata[source] = pickle.load(handle)

    def _embed_query(self, query: str) -> np.ndarray:
        embedding = self._model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]
        return np.asarray(embedding, dtype="float32")

    def _search(self, query: str, source: str, top_k: int) -> list[dict[str, Any]]:
        source = _normalize_source(source)
        index = self._indices[source]
        metadata = self._metadata[source]
        if index.ntotal == 0 or not metadata:
            return []

        query_vec = self._embed_query(query)
        search_k = min(max(top_k * 2, top_k), index.ntotal)
        distances, indices = index.search(np.asarray([query_vec], dtype="float32"), search_k)

        raw_results = []
        for match_index in indices[0]:
            if match_index < 0 or match_index >= len(metadata):
                continue
            raw_results.append(metadata[match_index])

        non_placeholder = [item for item in raw_results if not item.get("is_placeholder")]
        selected = non_placeholder[:top_k] if non_placeholder else raw_results[:top_k]

        return [
            {
                "text": item.get("text", ""),
                "source": item.get("source", item.get("relative_path", source)),
                "chunk_index": item.get("chunk_index", 0),
            }
            for item in selected
        ]

    def retrieve(self, query: str, source: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self._search(query=query, source=source, top_k=max(top_k, 1))

    def retrieve_all(self, query: str, provider: str, top_k: int = 5) -> list[dict[str, Any]]:
        provider_source = _normalize_source(provider)
        provider_results = self.retrieve(query=query, source=provider_source, top_k=top_k)
        compliance_results = self.retrieve(query=query, source="compliance", top_k=top_k)

        seen = set()
        combined = []
        for item in provider_results + compliance_results:
            key = (item["source"], item["chunk_index"], item["text"])
            if key in seen:
                continue
            seen.add(key)
            combined.append(item)
        return combined


def get_retriever() -> LocalDocsRetriever:
    global _RETRIEVER
    if _RETRIEVER is None:
        with _RETRIEVER_LOCK:
            if _RETRIEVER is None:
                _RETRIEVER = LocalDocsRetriever()
    return _RETRIEVER


def warm_retriever() -> LocalDocsRetriever:
    return get_retriever()
