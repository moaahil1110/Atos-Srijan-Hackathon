# Provider Docs

Nimbus uses local provider documentation for retrieval. The tracked files in this folder are the source documents that get chunked and embedded into the Azure and GCP FAISS indexes.

## Folder Layout

- `docs/providers/azure/`
- `docs/providers/gcp/`

## Azure Files

Expected files:

- `azure-storage.md`
- `azure-compute.md`
- `azure-virtual-network.md`
- `azure-key-vault.md`
- `azure-security-center.md`

These files cover:

- Azure Storage
- Azure Virtual Machines
- Azure Virtual Network
- Azure Key Vault
- Azure security and encryption guidance

## GCP Files

Expected files:

- `gcp-cloud-storage.md`
- `gcp-compute-engine.md`
- `gcp-vpc.md`
- `gcp-iam.md`
- `gcp-kms.md`

These files cover:

- Cloud Storage
- Compute Engine
- VPC and firewall policies
- IAM and service account guidance
- Cloud KMS and key rotation

## Rebuild Step

Whenever any provider document changes, rebuild the local indexes:

```bash
python scripts/build_index.py
```
