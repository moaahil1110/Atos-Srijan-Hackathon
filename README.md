# NIMBUS1000

NIMBUS1000 is a GenAI-powered cloud security copilot built with FastAPI and React. It reads a company description, extracts structured intent, computes deterministic security/compliance/cost weights, recommends provider-specific configurations, explains each field, analyzes gaps against existing configs, and exports Terraform.

## Supported Providers

- AWS
- Azure
- GCP

## Local Run

Backend:

```bash
cd backend
python run_dev.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Knowledge Base Sync

After uploading new compliance documents to `s3://nimbus-kb-documents/compliance/`, re-sync the Bedrock Knowledge Base:

`AWS Console -> Amazon Bedrock -> Knowledge Bases -> nimbus-compliance-kb -> Sync Data Source`
