# Person 1 (Aahil) — AI & Logic: Backend Documentation

> **Role**: AI & Logic — Everything that touches Bedrock and business logic  
> **Branch**: `feat-AI-Logic`  
> **Runtime**: FastAPI + Uvicorn (local dev) → Mangum (Lambda deployment)  
> **Goal**: By hour 4, `POST /intent` and `POST /config` must return real Bedrock-powered responses when curled locally on port 5000.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Files Owned by Person 1](#files-owned-by-person-1)
3. [Task 1: weights_engine.py](#task-1-weights_enginepy)
4. [Task 2: field_classifier.py](#task-2-field_classifierpy)
5. [Task 3: intent_service.py — Bedrock Intent Extraction](#task-3-intent_servicepy--bedrock-intent-extraction)
6. [Task 4: config_service.py — Config Generation with RAG](#task-4-config_servicepy--config-generation-with-rag)
7. [Task 5: explain_service.py — Conversational Counter-Asking](#task-5-explain_servicepy--conversational-counter-asking)
8. [Task 6: main.py — FastAPI + Mangum Wiring](#task-6-mainpy--fastapi--mangum-wiring)
9. [Supporting Files](#supporting-files)
10. [End-to-End Data Flow](#end-to-end-data-flow)
11. [Testing & Verification](#testing--verification)
12. [Dependencies on Person 2](#dependencies-on-person-2)

---

## Architecture Overview

```
                    ┌─────────────────────────────────────────┐
                    │         FastAPI (main.py)                │
                    │  CORS enabled, port 5000 local dev      │
                    │  Mangum handler for Lambda deployment    │
                    └───────┬──────┬──────┬──────┬────────────┘
                            │      │      │      │
                   ┌────────┘  ┌───┘  ┌───┘  ┌───┘
                   ▼           ▼      ▼      ▼
              POST /intent  POST   POST   POST
                           /schema /config /explain
                   │           │      │      │
                   ▼           ▼      ▼      ▼
            ┌──────────┐  ┌───────┐ ┌──────┐ ┌───────┐
            │ intent   │  │schema │ │config│ │explain│
            │ _service │  │_svc   │ │_svc  │ │_svc   │
            └────┬─────┘  └───┬───┘ └──┬───┘ └───┬───┘
                 │             │        │         │
        ┌────────┼─────────────┼────────┼─────────┤
        ▼        ▼             ▼        ▼         ▼
   ┌─────────┐ ┌──────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
   │weights  │ │field  │ │bedrock   │ │dynamo  │ │compliance│
   │_engine  │ │_class.│ │_client   │ │_client │ │_mapper   │
   │(pure py)│ │(pure) │ │(boto3)   │ │(boto3) │ │(S3+local)│
   └─────────┘ └──────┘ └──────────┘ └────────┘ └──────────┘
```

---

## Files Owned by Person 1

| File | Type | AWS Dependencies | Lines |
|------|------|-----------------|-------|
| `services/weights_engine.py` | Pure Python logic | None | 81 |
| `services/field_classifier.py` | Pure Python logic | None | 75 |
| `services/intent_service.py` | Bedrock service | Bedrock, DynamoDB | 82 |
| `services/config_service.py` | Bedrock service + RAG | Bedrock, DynamoDB, S3 | 126 |
| `services/explain_service.py` | Bedrock service | Bedrock, DynamoDB, S3 | 185 |
| `main.py` | FastAPI entry point | None (framework) | 51 |
| `models/intent.py` | Pydantic models | None | 17 |
| `models/config.py` | Pydantic models | None | 21 |
| `models/explain.py` | Pydantic models | None | 23 |
| `routers/intent.py` | API route | None | 18 |
| `routers/config.py` | API route | None | 24 |
| `routers/explain.py` | API route | None | 27 |

---

## Task 1: weights_engine.py

**File**: `services/weights_engine.py`  
**Type**: Pure Python — zero AWS dependencies  
**Purpose**: Convert a company profile (extracted by Bedrock) into deterministic priority weights.

### Function Signature

```python
def compute_weights(intent: dict) -> dict:
    # Returns {"security": float, "compliance": float, "cost": float}
    # All three values always sum to exactly 1.0
```

### Algorithm

**Step 1 — Security Score:**
- Starts at `0.40` (high base — this is a security-first advisor)
- Adds `(5 - riskTolerance) × 0.04` — lower risk tolerance = higher security
- Adds `0.08` if `dataClassification == "highly-confidential"`
- Capped at `0.70` maximum

**Step 2 — Compliance Score:**
- Starts at `0.00`
- If `complianceFrameworks` is not empty and not `["none"]`:
  - Base: `0.15`
  - Per extra framework: `+0.05 × (count - 1)`
  - If maturity is `"in-progress"`: `+0.10`
  - If maturity is `"not-started"`: `+0.05`

**Step 3 — Cost Score:**
- `(costPressure / 5) × 0.25`

**Step 4 — Normalization:**
- Divides each by the total sum so they add up to exactly `1.0`
- Fixes floating-point rounding errors

**Step 5 — Security Floor Enforcement:**
- If security drops below `0.40` after normalization:
  - Forces `security = 0.40`
  - Subtracts the deficit from cost first
  - If cost can't cover it, takes from compliance

### Test Results (8 Company Profiles)

| Company | Security | Compliance | Cost |
|---------|----------|------------|------|
| 🎮 Esports Betting (PCI-DSS + SOC2, risk 1) | 61.6% | 28.8% | 9.6% |
| 🌾 Farm IoT (no compliance, cost 5) | 61.5% | 0.0% | **38.5%** |
| 🧬 Biotech Gene Lab (HIPAA+GDPR+SOC2, risk 1) | 64.6% | **30.3%** | 5.1% |
| 🎪 Circus Tickets (PCI-DSS, risk 4, cost 4) | 52.4% | 23.8% | 23.8% |
| 🛰️ Satellite Defense (4 frameworks, risk 1) | 58.7% | **36.7%** | 4.6% |
| 🍕 Pizza Tracker (no compliance, cost 5) | 61.5% | 0.0% | **38.5%** |
| 🏥 Teletherapy (HIPAA certified, risk 1) | **68.0%** | 16.0% | 16.0% |
| ⛏️ Crypto Mining (SOC2, risk 3, cost 4) | 54.6% | 22.7% | 22.7% |

**Key observations**:
- Compliance swings from **0% → 36.7%** based on number of frameworks
- Cost swings from **4.6% → 38.5%** based on cost pressure
- Security is intentionally dominant (52-68%) — this is a security-first tool
- All rows sum to exactly **1.0**

---

## Task 2: field_classifier.py

**File**: `services/field_classifier.py`  
**Type**: Pure Python — zero AWS dependencies  
**Purpose**: Tag each AWS service field with an instruction that tells Bedrock how to configure it.

### Function Signature

```python
def classify_field(field: dict, weights: dict,
                   active_frameworks: list, maturity: str) -> dict:
    # Returns the original field dict with 3 added keys:
    #   instruction:       LOCKED_SECURE | PREFER_SECURE | OPTIMISE_COST | BALANCED
    #   effectivePriority: float
    #   complianceActive:  bool
```

### Instruction Tag Logic

| Tag | Condition | Meaning |
|-----|-----------|---------|
| `LOCKED_SECURE` | `securityRelevance == "critical"` | Most secure value, zero exceptions |
| `PREFER_SECURE` | `securityRelevance == "high"` AND `security_weight > 0.50` | Secure value strongly preferred |
| `OPTIMISE_COST` | `costRelevance == "high"` AND `cost_weight > 0.15` AND `securityRelevance == "none"` | Cost-efficient option permitted |
| `BALANCED` | Everything else | Use judgement based on profile |

### Effective Priority Calculation

```
priority  = security_weight × sec_multiplier(critical=1.0, high=0.7, medium=0.4)
          + compliance_weight × 0.8   (if field's complianceRelevance overlaps active frameworks)
          + cost_weight × cost_multiplier(high=1.0, medium=0.5)
```

### Compliance Boost (applied AFTER tag assignment)

- If compliance hit AND maturity `"in-progress"` → `priority × 1.6`
- If compliance hit AND maturity `"not-started"` → `priority × 1.4`

---

## Task 3: intent_service.py — Bedrock Intent Extraction

**File**: `services/intent_service.py`  
**Purpose**: The entry point of the entire pipeline. Takes a free-text company description and returns structured data.

### Flow

```
User Description (free text)
        │
        ▼
   Bedrock LLM  ──→  Structured JSON Profile
        │                 │
        │                 ▼
        │          compute_weights()
        │                 │
        ▼                 ▼
   Save to DynamoDB: {sessionId, companyProfile, computedWeights, conversationHistory: []}
        │
        ▼
   Return: {sessionId, intent, weights}
```

### Bedrock Prompt

The prompt instructs Bedrock to extract these exact fields from natural language:

| Field | Type | Example |
|-------|------|---------|
| `industry` | string | `"healthcare"`, `"logistics"` |
| `complianceFrameworks` | array | `["HIPAA"]`, `["PCI-DSS", "SOC2"]`, `[]` |
| `complianceMaturity` | enum | `"certified"`, `"in-progress"`, `"not-started"` |
| `teamSize` | string | `"20-person startup"` |
| `costPressure` | int 1-5 | `5` = max cost pressure |
| `riskTolerance` | int 1-5 | `1` = zero risk tolerance |
| `missionCriticalServices` | array | `["patient records", "billing"]` |
| `dataClassification` | enum | `"highly-confidential"`, `"confidential"`, `"internal"`, `"public"` |
| `weightReasoning` | string | LLM explains its reasoning for the scores |

### Safety Measures

- **Field defaults**: If Bedrock omits a field, sensible defaults are applied (`costPressure: 3`, `riskTolerance: 3`, etc.)
- **Integer clamping**: `costPressure` and `riskTolerance` are clamped to `[1, 5]` range
- **JSON parsing fallback**: `json.loads()` → regex extract `{...}` → retry with stricter prompt (3 attempts total)

---

## Task 4: config_service.py — Config Generation with RAG

**File**: `services/config_service.py`  
**Purpose**: Generate per-field configuration recommendations using Bedrock with compliance document context (RAG).

### Flow

```
{sessionId, schema, service}
        │
        ▼
   Load Session from DynamoDB (profile + weights)
        │
        ▼
   Classify each field (field_classifier)
        │
        ▼
   Fetch compliance docs from S3 (compliance_mapper — RAG)
        │
        ▼
   Build mega-prompt:
     • Enforced weights (security, compliance, cost)
     • Company profile (industry, risk, cost pressure)
     • Compliance reference text (actual clause text)
     • Classified fields (with instruction tags)
        │
        ▼
   Bedrock generates: {fieldId: {value, reason}}
        │
        ▼
   Save config to DynamoDB + Return
```

### Prompt Design (Key Rules for Bedrock)

1. **LOCKED_SECURE fields**: Most secure value, zero exceptions
2. **PREFER_SECURE fields**: Secure value strongly preferred
3. **OPTIMISE_COST fields**: Cost-efficient option permitted
4. **Security is NEVER relaxed for cost reasons**
5. **Reasons must be specific** — cite compliance clause numbers when available
   - ❌ BAD: `"Encryption is important for security"`
   - ✅ GOOD: `"HIPAA §164.312(e)(2)(ii) requires encryption of ePHI for your patient data workload"`

---

## Task 5: explain_service.py — Conversational Counter-Asking

**File**: `services/explain_service.py`  
**Purpose**: Allow users to challenge any config recommendation and have a multi-turn conversation with the AI advisor. Can dynamically update config values if the user's reasoning is valid.

### Flow

```
{sessionId, fieldId, fieldLabel, currentValue, inlineReason, message}
        │
        ▼
   Load session + conversation history from DynamoDB
        │
        ▼
   Fetch compliance doc for this field (S3)
        │
        ▼
   If first message for this field:
     Seed conversation with synthetic opening (inlineReason as assistant message)
        │
        ▼
   Append user message to per-field history
        │
        ▼
   Call Bedrock with:
     • System prompt (company context + compliance ref + rules)
     • Full conversation history for this field
        │
        ▼
   Parse response for UPDATE_FIELD signal
        │
        ├──→ No UPDATE_FIELD: return display text only
        │
        └──→ UPDATE_FIELD found:
              • Extract {fieldId, newValue, newReason}
              • Update generatedConfig in DynamoDB
              • Return display text + configUpdate
```

### UPDATE_FIELD Protocol

When Bedrock agrees that a field should be changed, it appends to its response:

```
UPDATE_FIELD: {"fieldId": "ServerSideEncryptionConfiguration", "newValue": "SSE-S3", "newReason": "SSE-S3 sufficient for internal data with no compliance requirements"}
```

The parser splits the response at `UPDATE_FIELD:`, shows the text portion to the user, and applies the JSON update to DynamoDB.

### Conversation Rules (System Prompt)

1. Don't repeat the inline reason — go deeper or address the user's concern
2. Tie responses to THIS company's specific context
3. `LOCKED_SECURE` field + user wants to relax → explain why not, suggest alternatives
4. Valid reason + adjustable field → suggest best alternative with `UPDATE_FIELD`
5. Keep responses to 3-4 sentences max
6. Never give generic advice

---

## Task 6: main.py — FastAPI + Mangum Wiring

**File**: `main.py`  
**Purpose**: Wire everything together into a running API server.

### API Routes

| Method | Path | Router | Description |
|--------|------|--------|-------------|
| `GET` | `/health` | inline | Health check → `{"status": "ok"}` |
| `POST` | `/intent` | `routers/intent.py` | Extract company profile + compute weights |
| `POST` | `/schema` | `routers/schema.py` | Load + classify schema fields |
| `POST` | `/config` | `routers/config.py` | Generate config with Bedrock + RAG |
| `POST` | `/explain` | `routers/explain.py` | Conversational counter-asking |
| `POST` | `/terraform` | `routers/terraform.py` | Stretch goal (501) |

### Configuration

- **CORS**: Enabled for all origins (development mode)
- **Local dev**: `uvicorn main:app --reload --port 5000`
- **Lambda**: `handler = Mangum(app)` — Mangum translates API Gateway events ↔ FastAPI
- **Auto-docs**: FastAPI generates Swagger UI at `/docs`

---

## Supporting Files

### Pydantic Models (`models/`)

| File | Request Body | Response Body |
|------|-------------|---------------|
| `models/intent.py` | `{description: str}` | `{sessionId, intent, weights}` |
| `models/config.py` | `{sessionId, schema, service}` | `{config: {fieldId: {value, reason}}}` |
| `models/explain.py` | `{sessionId, fieldId, fieldLabel, currentValue, inlineReason, message}` | `{response, configUpdate}` |

### Utility Clients (`utils/`) — Thin Wrappers

| File | Purpose | Person 2 owns the infrastructure |
|------|---------|--------------------------------|
| `utils/bedrock_client.py` | Converse API wrapper + JSON parsing with retry | Bedrock model access |
| `utils/dynamo_client.py` | get/save/update session | DynamoDB table creation |
| `utils/s3_client.py` | get/put object | S3 bucket setup |
| `utils/compliance_mapper.py` | Maps (framework, field_keyword) → compliance doc text | Real compliance doc content |

### Config (`config.py`)

Environment variables with defaults:

| Variable | Default |
|----------|---------|
| `AWS_REGION` | `us-east-1` |
| `DYNAMO_TABLE` | `nimbus-sessions` |
| `S3_BUCKET` | `nimbus-compliance-docs` |
| `BEDROCK_MODEL_ID` | `us.anthropic.claude-3-5-sonnet-20241022-v2:0` |

---

## End-to-End Data Flow

```
Step 1: POST /intent
  User: "We're a 20-person healthcare startup. HIPAA in-progress. Security non-negotiable."
  → Bedrock extracts: {industry: "healthcare", riskTolerance: 1, costPressure: 2, ...}
  → weights_engine: {security: 0.646, compliance: 0.253, cost: 0.101}
  → DynamoDB: session saved
  → Response: {sessionId: "abc-123", intent: {...}, weights: {...}}

Step 2: POST /schema
  {sessionId: "abc-123", service: "S3", provider: "aws"}
  → Load S3 schema fields
  → field_classifier tags each field (LOCKED_SECURE, etc.)
  → Response: {schema: {fields: [{fieldId: "...", instruction: "LOCKED_SECURE", ...}]}}

Step 3: POST /config
  {sessionId: "abc-123", schema: {...}, service: "S3"}
  → Load session weights + profile
  → Fetch HIPAA compliance docs (RAG)
  → Bedrock generates: {ServerSideEncryption: {value: "SSE-KMS", reason: "HIPAA §164.312..."}}
  → Response: {config: {...}}

Step 4: POST /explain
  {sessionId: "abc-123", fieldId: "ServerSideEncryption", message: "Can we use SSE-S3?"}
  → Multi-turn conversation with context
  → If valid: UPDATE_FIELD signal updates config
  → Response: {response: "...", configUpdate: {newValue: "SSE-S3", ...}}
```

---

## Testing & Verification

### Running Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 5000
```

### Curl Commands

```bash
# Test intent extraction
curl -s -X POST http://localhost:5000/intent \
  -H "Content-Type: application/json" \
  -d '{"description": "20-person healthcare startup storing patient records. HIPAA in-progress. Security is non-negotiable."}' | python -m json.tool

# Test config generation (use sessionId from above)
curl -s -X POST http://localhost:5000/config \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "SESSION_ID_HERE", "schema": {...}, "service": "S3"}' | python -m json.tool

# Test explain
curl -s -X POST http://localhost:5000/explain \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "fieldId": "ServerSideEncryptionConfiguration", "fieldLabel": "Server-side encryption", "currentValue": "SSE-KMS", "inlineReason": "HIPAA requires...", "message": "Can we use SSE-S3 instead?"}' | python -m json.tool
```

### Unit Tests (Pure Python — No AWS Needed)

All pure-Python modules were tested with assertions:
- `weights_engine`: Tested across 8 diverse company profiles — all sum to 1.0 ✓
- `field_classifier`: Verified instruction tags and compliance boosts ✓
- All 27 Python files compile without errors ✓

---

## Dependencies on Person 2

| What I Need From Person 2 | Why |
|---------------------------|-----|
| DynamoDB table `nimbus-sessions` (partition key: `sessionId`) | Sessions are stored/retrieved here |
| S3 bucket with real compliance docs at `compliance/*.txt` | RAG — Bedrock cites these in config reasons |
| 3 pre-cached schema JSONs (S3, RDS, IAM) with real field definitions | `field_classifier` needs real `securityRelevance`, `costRelevance`, etc. |
| AWS credentials configured | Bedrock, DynamoDB, S3 calls |
| End-to-end curl testing after infrastructure is up | Validate full pipeline with real AWS services |
