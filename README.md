# Nimbus

Nimbus is a cloud configuration advisor that recommends and optimizes Azure and GCP service settings using company context, compliance requirements, and locally indexed provider documentation.

## What Reviewers Need To Know

- The repository does not include AWS credentials, Bedrock credentials, DynamoDB credentials, or Firebase environment values.
- The repository does include the compliance corpus and the provider documentation used for local retrieval.
- Bedrock is used only for model inference.
- Retrieval is local and runs from FAISS indexes built from the documents in `docs/compliance` and `docs/providers`.

## Architecture

```text
User -> Frontend (React)
          |
          v
     Backend (FastAPI)
       |- Local FAISS retrieval
       |   |- Compliance docs
       |   |- Azure docs
       |   `- GCP docs
       |
       v
 AWS Bedrock (inference only)
       |
       v
 AWS DynamoDB (sessions + decision evidence)
```

## Repository Layout

```text
backend/              FastAPI app, services, Bedrock client, DynamoDB client
frontend/             React app
docs/compliance/      Compliance source documents tracked in Git
docs/providers/       Azure and GCP provider docs tracked in Git
docs/project/         Internal architecture and implementation notes
scripts/              Utility scripts such as FAISS index building
tests/                Evaluation runner and optional local test utilities
requirements.txt      Backend Python dependencies
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- An AWS account with:
  - Bedrock model access
  - DynamoDB access
- A Firebase project for frontend authentication

## Backend Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in the AWS values.

3. Build the local indexes:

```bash
python scripts/build_index.py
```

4. Start the backend:

```bash
cd backend
python run_dev.py
```

The backend runs on `http://127.0.0.1:5000` by default.

## Frontend Setup

1. Copy `frontend/.env.example` to `frontend/.env` and fill in your Firebase values.

2. Install dependencies:

```bash
cd frontend
npm install
```

3. Start the frontend:

```bash
npm run dev
```

## Environment Variables

### Root `.env`

These are the backend variables Nimbus expects:

| Variable | Required | Purpose |
|---|---|---|
| `AWS_REGION` | Yes | AWS region for Bedrock and DynamoDB |
| `DYNAMODB_TABLE_NAME` | Yes | Session storage table |
| `BEDROCK_MODEL_ID` | Yes | Bedrock model or inference profile ARN |
| `AWS_ACCESS_KEY_ID` | Yes | AWS credentials for DynamoDB |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS credentials for DynamoDB |
| `AWS_SESSION_TOKEN` | No | Optional temporary AWS session token |
| `BEDROCK_AWS_ACCESS_KEY_ID` | No | Optional Bedrock-specific credentials |
| `BEDROCK_AWS_SECRET_ACCESS_KEY` | No | Optional Bedrock-specific credentials |
| `BEDROCK_AWS_SESSION_TOKEN` | No | Optional Bedrock-specific session token |
| `EMBEDDING_MODEL` | No | Defaults to `all-MiniLM-L6-v2` |
| `COMPLIANCE_INDEX_PATH` | No | Defaults to `embeddings/compliance_index` |
| `AZURE_INDEX_PATH` | No | Defaults to `embeddings/azure_index` |
| `GCP_INDEX_PATH` | No | Defaults to `embeddings/gcp_index` |
| `COMPLIANCE_DOCS_DIR` | No | Defaults to `docs/compliance` |
| `AZURE_DOCS_DIR` | No | Defaults to `docs/providers/azure` |
| `GCP_DOCS_DIR` | No | Defaults to `docs/providers/gcp` |

### Frontend `frontend/.env`

The frontend expects Firebase Vite variables:

- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`
- `VITE_FIREBASE_MEASUREMENT_ID`

## Documents Included In Git

Nimbus ships with the local documents reviewers need for retrieval:

- `docs/compliance/hipaa`
- `docs/compliance/pci-dss`
- `docs/compliance/soc2`
- `docs/compliance/gdpr`
- `docs/compliance/iso27001`
- `docs/providers/azure`
- `docs/providers/gcp`

If you update any document, rebuild the indexes with:

```bash
python scripts/build_index.py
```

## Notes For Reviewers

- No cloud-provider selector is required in the UI. Provider preference is inferred from the user’s written context.
- Terraform appears only after a grounded configuration has been generated.
- Decision evidence is stored in DynamoDB and reused during follow-up explanation flows.
- Generated embeddings are not committed; reviewers should rebuild them locally.

## License

MIT
