# Docs Overview

This `docs/` directory is split into three parts:

- `docs/compliance/`
  The compliance source corpus used for FAISS retrieval.
- `docs/providers/`
  The Azure and GCP provider documentation used for FAISS retrieval.
- `docs/project/`
  Internal project notes, architecture writeups, and planning material.

## Retrieval Sources

Nimbus builds local indexes from:

- `docs/compliance`
- `docs/providers/azure`
- `docs/providers/gcp`

After changing any of those files, rebuild the indexes:

```bash
python scripts/build_index.py
```
