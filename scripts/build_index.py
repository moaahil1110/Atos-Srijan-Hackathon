from __future__ import annotations

import os
import pickle
import re
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

try:
    import faiss  # type: ignore
except ImportError as exc:  # pragma: no cover - depends on environment
    raise ImportError(
        "faiss-cpu is required to build local indexes. Install backend dependencies first."
    ) from exc

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=False)
load_dotenv(ROOT_DIR / "backend" / ".env", override=True)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COMPLIANCE_INDEX_PATH = os.getenv("COMPLIANCE_INDEX_PATH", "embeddings/compliance_index")
AZURE_INDEX_PATH = os.getenv("AZURE_INDEX_PATH", "embeddings/azure_index")
GCP_INDEX_PATH = os.getenv("GCP_INDEX_PATH", "embeddings/gcp_index")

SOURCE_DIRS = {
    "compliance": ROOT_DIR / "docs" / "compliance",
    "azure": ROOT_DIR / "docs" / "providers" / "azure",
    "gcp": ROOT_DIR / "docs" / "providers" / "gcp",
}
INDEX_PATHS = {
    "compliance": COMPLIANCE_INDEX_PATH,
    "azure": AZURE_INDEX_PATH,
    "gcp": GCP_INDEX_PATH,
}
SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown"}
PLACEHOLDER_MARKER = "Replace this file with the actual"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def resolve_output_base(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT_DIR / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def tokenize(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    tokens = tokenize(text)
    if not tokens:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(tokens), step):
        window = tokens[start : start + chunk_size]
        if not window:
            continue
        chunks.append(" ".join(window))
        if start + chunk_size >= len(tokens):
            break
    return chunks


def read_documents(source_name: str, directory: Path) -> tuple[list[dict], int]:
    documents = []
    placeholder_count = 0

    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = path.read_text(encoding="utf-8")
        is_placeholder = PLACEHOLDER_MARKER in text.splitlines()[0] if text.splitlines() else False
        if is_placeholder:
            placeholder_count += 1

        chunk_list = chunk_text(text)
        for chunk_index, chunk in enumerate(chunk_list):
            documents.append(
                {
                    "source_name": source_name,
                    "source": str(path.relative_to(ROOT_DIR)).replace("\\", "/"),
                    "source_filename": path.name,
                    "relative_path": str(path.relative_to(ROOT_DIR)).replace("\\", "/"),
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "is_placeholder": is_placeholder,
                }
            )

    return documents, placeholder_count


def build_source_index(source_name: str, docs: list[dict], model: SentenceTransformer) -> tuple[int, int]:
    output_base = resolve_output_base(INDEX_PATHS[source_name])
    index_path = output_base.with_suffix(".faiss")
    metadata_path = output_base.with_suffix(".pkl")

    embeddings = model.encode(
        [doc["text"] for doc in docs],
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(np.asarray(embeddings, dtype="float32"))

    faiss.write_index(index, str(index_path))
    with metadata_path.open("wb") as handle:
        pickle.dump(docs, handle)

    return len(docs), index.ntotal


def main() -> None:
    print(f"Using embedding model: {EMBEDDING_MODEL}")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL, local_files_only=True)
    except Exception:
        model = SentenceTransformer(EMBEDDING_MODEL)

    total_docs = 0
    total_chunks = 0

    for source_name, directory in SOURCE_DIRS.items():
        if not directory.exists():
            raise FileNotFoundError(f"Document directory not found for {source_name}: {directory}")

        docs, placeholder_count = read_documents(source_name, directory)
        if not docs:
            raise RuntimeError(f"No documents found for {source_name} in {directory}")

        doc_count = len({doc["source"] for doc in docs})
        chunk_count, index_size = build_source_index(source_name, docs, model)
        total_docs += doc_count
        total_chunks += chunk_count

        print(
            f"[{source_name}] docs processed: {doc_count}, chunks: {chunk_count}, "
            f"index size: {index_size}, placeholders: {placeholder_count}"
        )

    print(
        f"Completed index rebuild. Total docs processed: {total_docs}. "
        f"Total chunks: {total_chunks}."
    )


if __name__ == "__main__":
    main()
