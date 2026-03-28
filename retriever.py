"""
Nimbus RAG Retriever
---------------------
Loads the compliance_embeddings.jsonl and retrieves the most relevant
chunks for a given query. Called by the backend before building prompts.

Usage in backend services:
    from retriever import ComplianceRetriever

    retriever = ComplianceRetriever("compliance_embeddings.jsonl")

    # Get context for a specific decision
    results = retriever.retrieve(
        query="S3 encryption at rest for patient health records",
        framework="hipaa",       # optional — filter by framework
        topic="encryption",      # optional — filter by topic
        top_k=4
    )

    # Each result has: text, metadata, score
    context = "\n\n".join(r["text"] for r in results)
    # Inject context into your Bedrock prompt
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional


class ComplianceRetriever:
    def __init__(self, jsonl_path: str):
        self.chunks = []
        self.embeddings = []
        self._load(jsonl_path)

    def _load(self, path: str):
        print(f"Loading embeddings from {path}...")
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                chunk = json.loads(line)
                self.embeddings.append(chunk["embedding"])
                self.chunks.append({k: v for k, v in chunk.items() if k != "embedding"})

        self.embeddings = np.array(self.embeddings, dtype=np.float32)
        print(f"Loaded {len(self.chunks)} chunks")

    def _embed_query(self, query: str) -> np.ndarray:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("Run: pip install sentence-transformers")

        if not hasattr(self, "_model"):
            self._model = SentenceTransformer("all-MiniLM-L6-v2")

        vec = self._model.encode([query], normalize_embeddings=True)[0]
        return np.array(vec, dtype=np.float32)

    def retrieve(
        self,
        query: str,
        framework: Optional[str] = None,
        topic: Optional[str] = None,
        top_k: int = 5
    ) -> list:
        """
        Retrieve top_k most relevant compliance chunks for a query.

        Args:
            query:      natural language question or field description
            framework:  filter by compliance framework e.g. "hipaa", "pci-dss"
            topic:      filter by topic e.g. "encryption", "logging"
            top_k:      number of chunks to return

        Returns:
            list of dicts: { text, metadata, score }
            sorted by relevance score descending
        """
        query_vec = self._embed_query(query)

        # Compute cosine similarity (vectors are normalised so dot product = cosine)
        scores = self.embeddings @ query_vec  # shape: (n_chunks,)

        # Apply metadata filters — restrict candidate pool
        mask = np.ones(len(self.chunks), dtype=bool)
        if framework:
            fw = framework.lower().replace(" ", "-")
            mask &= np.array([
                c["metadata"]["framework"] == fw
                for c in self.chunks
            ])
        if topic:
            tp = topic.lower().replace(" ", "-")
            mask &= np.array([
                c["metadata"]["topic"] == tp
                for c in self.chunks
            ])

        # If filters leave nothing, fall back to no filter
        if mask.sum() == 0:
            mask = np.ones(len(self.chunks), dtype=bool)

        filtered_indices = np.where(mask)[0]
        filtered_scores  = scores[filtered_indices]

        # Top-k
        top_local = np.argsort(filtered_scores)[::-1][:top_k]
        top_global = filtered_indices[top_local]

        results = []
        for idx in top_global:
            results.append({
                "text":     self.chunks[idx]["text"],
                "metadata": self.chunks[idx]["metadata"],
                "score":    float(scores[idx])
            })

        return results

    def get_context_for_prompt(
        self,
        query: str,
        framework: Optional[str] = None,
        topic: Optional[str] = None,
        top_k: int = 4,
        max_words: int = 600
    ) -> str:
        """
        Returns a single string ready to inject into a Bedrock prompt.
        Truncates to max_words total to keep prompt size manageable.
        """
        results = self.retrieve(query, framework=framework, topic=topic, top_k=top_k)

        parts = []
        word_count = 0
        for r in results:
            words = r["text"].split()
            if word_count + len(words) > max_words:
                remaining = max_words - word_count
                if remaining > 30:
                    parts.append(" ".join(words[:remaining]))
                break
            parts.append(r["text"])
            word_count += len(words)
            meta = r["metadata"]
            source_note = f"[{meta['framework'].upper()} — {meta['topic']} — {meta['source']}]"
            parts.append(source_note)

        return "\n\n".join(parts)


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    jsonl = sys.argv[1] if len(sys.argv) > 1 else "compliance_embeddings.jsonl"

    if not Path(jsonl).exists():
        print(f"File not found: {jsonl}")
        print("Run ingest.py first to generate the embeddings file.")
        sys.exit(1)

    retriever = ComplianceRetriever(jsonl)

    # Test queries
    test_cases = [
        ("S3 encryption at rest for patient health records", "hipaa",    "encryption"),
        ("access control for cardholder data",               "pci-dss",  "access-control"),
        ("audit logs and monitoring requirements",            "soc2",     "logging"),
        ("data retention policy for personal data",          "gdpr",     "data-retention"),
        ("backup and disaster recovery",                     None,        None),
    ]

    for query, fw, tp in test_cases:
        print(f"\nQuery: {query}")
        print(f"Filter: framework={fw}, topic={tp}")
        results = retriever.retrieve(query, framework=fw, topic=tp, top_k=2)
        for r in results:
            print(f"  [{r['score']:.3f}] {r['metadata']['framework']} / {r['metadata']['topic']} — {r['text'][:120]}...")
