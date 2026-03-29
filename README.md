# Nimbus — AI-Powered Cloud Security Co-Pilot

> *Configure once. Configure right. Never compromise on security.*

---

## What is Nimbus?

Nimbus is an intelligent cloud configuration advisor that generates, reviews, and optimizes cloud infrastructure settings tailored to a company's context rather than generic best practices.

It combines provider documentation, company context, and compliance-oriented retrieval to help teams make safer configuration decisions for AWS, Azure, and GCP services.

---

## Why Nimbus is Different

### The Problem with General LLMs

General-purpose AI models are useful for exploration, but cloud configuration needs tighter grounding than a long free-form conversation usually provides. If priorities drift over time, the resulting recommendation can drift too.

### The Nimbus Approach

Nimbus grounds its recommendations in three inputs:

```text
1. Provider Documentation
2. Company Context
3. Compliance Requirements
```

In practice, the backend assembles prompts from local provider and compliance retrieval plus structured company context before asking the model for a decision. The goal is to keep recommendations anchored to the retrieved evidence instead of relying on broad model recall.

Think of it like a doctor who checks the literature, the patient's context, and the relevant rules before giving an answer. Nimbus applies that same pattern to cloud configuration.

---

## What Nimbus Does

### Company-Aware Configuration

Nimbus takes a company description and extracts structured context such as industry, compliance frameworks, data sensitivity, risk tolerance, and cost pressure. A healthcare startup and a fintech enterprise should not receive the same defaults.

### Recommendation

Given a company profile, Nimbus recommends a cloud provider and service mix, then generates grounded configuration values for the selected services.

### Optimization

If you already have a cloud setup, Nimbus can compare an uploaded or pasted JSON configuration against the recommended posture for a service and highlight gaps, recommended values, and the reasoning behind them.

### Grounded Explanations

Every configuration field can be followed up on in the chat flow using the same company and retrieval context that informed the recommendation.

### Terraform Export

Once a configuration is prepared, Nimbus can generate Terraform output for the selected service.

---

## How It Works Under the Hood

```text
User Input (Company Description + Optional Current Config)
                        ↓
              Backend — Intent Extraction
         (industry, compliance, risk, cost weights)
                        ↓
         ┌──────────────────────────────────┐
         │     Context Assembly Layer       │
         │  ┌────────────────────────────┐  │
         │  │ 1. Provider Docs (FAISS)   │  │
         │  │    AWS / Azure / GCP       │  │
         │  │ 2. Company Context         │  │
         │  │ 3. Compliance Docs (FAISS) │  │
         │  │    HIPAA / PCI-DSS / SOC2  │  │
         │  └────────────────────────────┘  │
         └──────────────────────────────────┘
                        ↓
              AWS Bedrock LLM (Inference)
              [Grounded prompt assembly]
                        ↓
         Config Output + Reasoning + Evidence
                        ↓
         DynamoDB Session Storage
                        ↓
         Frontend — Results / Follow-up / Terraform
```

All retrieval decisions are made in the backend. The model receives assembled context from provider docs, compliance docs, and company context before generating output.

---

## Knowledge Base

Nimbus is grounded in multiple layers of documentation:

| Layer | Source | Purpose |
|---|---|---|
| AWS Documentation | Official AWS docs gathered locally | Service configs, field definitions, security guidance |
| Azure Documentation | Microsoft Learn pages gathered locally | Azure service behavior and security controls |
| GCP Documentation | Google Cloud docs gathered locally | GCP service behavior and recommended settings |
| Compliance Frameworks | HIPAA, PCI-DSS, SOC2, GDPR, ISO27001 | Regulatory requirements and compliance grounding |

Documents are chunked, embedded locally with `sentence-transformers`, and indexed with FAISS for retrieval.

---

## Services Used

| Service | Role |
|---|---|
| **AWS Bedrock** | LLM inference engine for recommendation, optimization, and explanation flows |
| **AWS DynamoDB** | Session storage and persisted conversation/config state |
| **FAISS (local)** | Vector similarity search across provider and compliance docs |
| **sentence-transformers** | Local embedding generation |
| **Firebase Auth** | Frontend authentication |
| **React** | Frontend workspace UI |
| **FastAPI** | Backend API, orchestration, retrieval, and prompt assembly |

---

## Team — Star Trek

| Name | Contribution |
|---|---|
| **Muhammad Shehzaad Khan** | Backend architecture, FAISS retrieval integration, prompt engineering, frontend UI logic, end-to-end system integration |
| **Musharraf** | AWS infrastructure, DynamoDB setup, Bedrock access, IAM and credentials management |
| **Aahil** | Compliance document collection and curation, provider doc sourcing |
| **Mir** | Document ingestion pipeline, chunking strategy, embedding generation, index structure |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- AWS account with Bedrock and DynamoDB access
- Firebase project for frontend authentication

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd nimbus

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Configure backend environment
cp .env.example .env

# Configure frontend environment
cp frontend/.env.example frontend/.env

# Build local document indexes
python scripts/build_index.py

# Start backend
cd backend
python run_dev.py

# Start frontend
cd ../frontend
npm run dev
```

The backend runs on `http://127.0.0.1:5000` by default.

---

## Environment Variables

### Root `.env`

| Variable | Description |
|---|---|
| `APP_HOST` | Backend host |
| `APP_PORT` | Backend port |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `AWS_SESSION_TOKEN` | Optional temporary AWS session token |
| `AWS_REGION` | AWS region |
| `BEDROCK_MODEL_ID` | Bedrock model identifier or inference profile ARN |
| `BEDROCK_AWS_ACCESS_KEY_ID` | Optional Bedrock-specific access key |
| `BEDROCK_AWS_SECRET_ACCESS_KEY` | Optional Bedrock-specific secret |
| `BEDROCK_AWS_SESSION_TOKEN` | Optional Bedrock-specific session token |
| `BEDROCK_CONNECT_TIMEOUT` | Bedrock client connect timeout |
| `BEDROCK_READ_TIMEOUT` | Bedrock client read timeout |
| `DYNAMODB_TABLE_NAME` | Session storage table name |
| `EMBEDDING_MODEL` | Local embedding model |
| `COMPLIANCE_INDEX_PATH` | Path to compliance FAISS index |
| `AZURE_INDEX_PATH` | Path to Azure docs FAISS index |
| `GCP_INDEX_PATH` | Path to GCP docs FAISS index |
| `AWS_INDEX_PATH` | Path to AWS docs FAISS index |
| `COMPLIANCE_DOCS_DIR` | Compliance docs directory |
| `AZURE_DOCS_DIR` | Azure docs directory |
| `GCP_DOCS_DIR` | GCP docs directory |
| `AWS_DOCS_DIR` | AWS docs directory |

### Frontend `frontend/.env`

| Variable | Description |
|---|---|
| `VITE_FIREBASE_API_KEY` | Firebase config |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase config |
| `VITE_FIREBASE_PROJECT_ID` | Firebase config |
| `VITE_FIREBASE_STORAGE_BUCKET` | Firebase config |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Firebase config |
| `VITE_FIREBASE_APP_ID` | Firebase config |
| `VITE_FIREBASE_MEASUREMENT_ID` | Firebase config |

---

## Refreshing Documentation

To refresh provider documentation and rebuild the local indexes:

```bash
python scripts/fetch_provider_docs.py
python scripts/build_index.py
```

---

## Security Philosophy

Nimbus is built around one core idea:

> **Security is not a setting. It is a constraint.**

Cost can be optimized and configurations can be compared, but the system is designed to start from provider- and compliance-grounded recommendations rather than generic convenience defaults.

---

## Notes For Reviewers

- The repository does not include real AWS credentials, Bedrock credentials, DynamoDB credentials, or Firebase environment values.
- Local provider and compliance source documents are tracked in the repository for retrieval workflows.
- Retrieval is local and uses FAISS indexes built from those documents.
- Terraform export is available after a grounded configuration has been generated for a service.
