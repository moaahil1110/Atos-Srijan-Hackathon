from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from backend.utils.local_retrieval import get_retriever, warm_retriever


def retrieve(query: str, source: str, top_k: int = 5) -> list[dict]:
    return get_retriever().retrieve(query=query, source=source, top_k=top_k)


def retrieve_all(query: str, provider: str, top_k: int = 5) -> list[dict]:
    return get_retriever().retrieve_all(query=query, provider=provider, top_k=top_k)


class ComplianceRetriever:
    def __init__(self, *_args, **_kwargs):
        self._retriever = get_retriever()

    def retrieve(
        self,
        query: str,
        framework: Optional[str] = None,
        topic: Optional[str] = None,
        top_k: int = 5,
    ) -> list[dict]:
        search_query = " ".join(part for part in [query, framework, topic] if part)
        return self._retriever.retrieve(query=search_query, source="compliance", top_k=top_k)

    def get_context_for_prompt(
        self,
        query: str,
        framework: Optional[str] = None,
        topic: Optional[str] = None,
        top_k: int = 4,
        max_words: int = 600,
    ) -> str:
        results = self.retrieve(query=query, framework=framework, topic=topic, top_k=top_k)
        parts = []
        word_count = 0
        for item in results:
            words = item["text"].split()
            if word_count + len(words) > max_words:
                remaining = max_words - word_count
                if remaining > 20:
                    parts.append(" ".join(words[:remaining]))
                break
            parts.append(f"Source: {item['source']} (chunk {item['chunk_index']})\n{item['text']}")
            word_count += len(words)
        return "\n\n".join(parts)


if __name__ == "__main__":
    import sys

    try:
        warm_retriever()
    except Exception as exc:  # pragma: no cover - manual CLI path
        print(str(exc))
        raise SystemExit(1) from exc

    query = sys.argv[1] if len(sys.argv) > 1 else "HIPAA encryption requirements for cloud storage"
    provider = sys.argv[2] if len(sys.argv) > 2 else "azure"
    results = retrieve_all(query=query, provider=provider, top_k=3)
    print(json.dumps(results, indent=2))
