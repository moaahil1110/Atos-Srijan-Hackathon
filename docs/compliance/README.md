# Compliance Corpus

These files are the local compliance knowledge base used by Nimbus retrieval.

## Structure

- `hipaa/`
- `pci-dss/`
- `soc2/`
- `gdpr/`
- `iso27001/`

Each folder contains topic-specific text files such as:

- access control
- encryption
- logging
- backup and recovery
- identity and authentication
- network protection
- audit evidence
- data retention

`inventory.txt` lists the collected documents at a high level.

If you edit or replace any compliance file, rebuild the indexes:

```bash
python scripts/build_index.py
```
