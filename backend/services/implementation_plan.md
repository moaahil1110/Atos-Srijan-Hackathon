# Person 1 — AI & Logic: Implementation Plan

## Goal
By **hour 4**, `POST /intent` and `POST /config` must return real Bedrock-powered responses when curled locally on port 5000.

**Runtime**: FastAPI + uvicorn (local dev) → Mangum (Lambda deployment)

---

## Task 1: [services/weights_engine.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/weights_engine.py)

Pure Python. No AWS. Deterministic — same input always gives same output.

### Function

```python
def compute_weights(intent: dict) -> dict:
```

### Algorithm

**Security score:**
```
start = 0.40
add (5 - riskTolerance) × 0.04
if dataClassification == "highly-confidential": add 0.08
cap at 0.70
```

**Compliance score:**
```
start = 0.00
if complianceFrameworks is not empty and not ["none"]:
    set to 0.15
    add 0.05 × (number_of_frameworks - 1)
    if complianceMaturity == "in-progress": add 0.10
    if complianceMaturity == "not-started": add 0.05
```

**Cost score:**
```
(costPressure / 5) × 0.25
```

**Normalise:** divide each by `(security + compliance + cost)`, round to 3 decimal places.

**Final enforcement:** if security < 0.40 after normalisation:
- `deficit = 0.40 - security`, force `security = 0.40`
- Subtract deficit from cost first; if cost can't cover it, subtract from compliance

### Test Cases

| Company | Expected Output |
|---------|----------------|
| Healthcare — HIPAA in-progress, risk 1, cost 2 | `{security: 0.62, compliance: 0.28, cost: 0.10}` |
| E-commerce — no compliance, risk 4, cost 5 | `{security: 0.50, compliance: 0.00, cost: 0.25}` |

---

## Task 2: [services/field_classifier.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/field_classifier.py)

Pure Python. No AWS.

### Function

```python
def classify_field(field: dict, weights: dict,
                   active_frameworks: list, maturity: str) -> dict:
```

### Algorithm

**Compute `effective_priority`:**
- `securityRelevance == "critical"` → add `weights["security"] × 1.0`
- `"high"` → `× 0.7`, `"medium"` → `× 0.4`
- If field's `complianceRelevance` overlaps `active_frameworks` (compliance_hit=True) → add `weights["compliance"] × 0.8`
- `costRelevance == "high"` → add `weights["cost"] × 1.0`, `"medium"` → `× 0.5`

**Assign instruction tag:**
- `securityRelevance == "critical"` → `LOCKED_SECURE`
- `securityRelevance == "high"` AND `weights["security"] > 0.50` → `PREFER_SECURE`
- `costRelevance == "high"` AND `weights["cost"] > 0.15` AND `securityRelevance == "none"` → `OPTIMISE_COST`
- Everything else → `BALANCED`

**Compliance boost (after tag assignment):**
- If compliance_hit AND maturity `"in-progress"` → multiply `effective_priority × 1.6`
- If compliance_hit AND maturity `"not-started"` → multiply `effective_priority × 1.4`

**Return** the original field dict with 3 added keys: `instruction`, `effectivePriority`, `complianceActive`.

---

## Task 3: [services/intent_service.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/intent_service.py) — Bedrock Intent Extraction

### Flow

1. Call Bedrock with company description → get structured JSON profile
2. Call `compute_weights(profile)` → get `{security, compliance, cost}`
3. Generate `sessionId` via `uuid4()`
4. Save to DynamoDB: `{sessionId, companyProfile, computedWeights, conversationHistory: [], createdAt}`
5. Return `{sessionId, intent, weights}`

### Bedrock Prompt

```
Extract structured business context from this company description.
Return ONLY valid JSON with these exact fields:
  industry, complianceFrameworks (array), complianceMaturity,
  teamSize, costPressure (1-5 integer), riskTolerance (1-5 integer),
  missionCriticalServices (array), dataClassification, weightReasoning

Hard rules:
- costPressure and riskTolerance must be integers 1 to 5
- complianceFrameworks must be an array even if empty
- If no compliance mentioned, use empty array []
- Return ONLY the JSON object, no preamble

Company description:
{description}
```

### JSON Parsing Strategy

```python
# Try json.loads(response) first
# If fails: regex extract first { ... } block
# If still fails: retry Bedrock with stricter prompt
```

---

## Task 4: [services/config_service.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/config_service.py) — Config Generation (with RAG)

### Flow

1. Fetch session from DynamoDB → `companyProfile`, `computedWeights`
2. Fetch compliance text from S3 → use `compliance_mapper` to find matching [.txt](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/requirements.txt) files
3. Build prompt with weights + company profile + compliance text + classified fields
4. Call Bedrock → parse `{fieldId: {value, reason}}` JSON map
5. Save `generatedConfig` + `selectedService` to DynamoDB
6. Return config map

### Bedrock Prompt

```
You are configuring AWS {service} for a specific company.

ENFORCED priority weights — computed by backend, do not override:
  Security: {weights.security}
  Compliance: {weights.compliance}
  Cost: {weights.cost}

Company profile:
  Industry: {intent.industry}
  Compliance: {frameworks} ({maturity})
  Cost pressure: {costPressure}/5
  Risk tolerance: {riskTolerance}/5
  Weight reasoning: {weightReasoning}

Compliance reference text:
{compliance_text_from_s3}

Fields to configure:
{json list of fields with instruction tags}

Return ONLY a JSON object where each key is a fieldId and each value
is an object with exactly two keys:
  value: the recommended setting (boolean, string, or number)
  reason: one sentence — must be specific to this company, must cite
          compliance clause number if reference text contains one

Critical rules:
- LOCKED_SECURE fields: most secure value, zero exceptions
- PREFER_SECURE fields: secure value strongly preferred
- OPTIMISE_COST fields: cost-efficient option permitted
- BALANCED fields: use judgement based on profile
- Security is NEVER relaxed for cost reasons
- BAD reason: "Encryption is important for security"
- GOOD reason: "HIPAA §164.312(e)(2)(ii) requires encryption of ePHI
                for your patient data workload"
```

### RAG Integration

```python
# compliance_mapper does this lookup:
# ("HIPAA", "encryption") → "compliance/hipaa-encryption.txt"
# ("HIPAA", "access")     → "compliance/hipaa-access-controls.txt"
# Then s3_client.get_object(bucket, key) → raw text string
# Concatenate all matching docs into one compliance_text block
```

---

## Task 5: [services/explain_service.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/explain_service.py) — Conversational Counter-Asking

### Flow

1. Load session from DynamoDB → full session including `conversationHistory`
2. Fetch matching compliance doc from S3 (same mapper as config_service)
3. If no conversation exists for this `fieldId`, seed with synthetic opening:
   `{role: "assistant", content: inlineReason, fieldId: fieldId}`
4. Append user message: `{role: "user", content: message, fieldId: fieldId}`
5. Call Bedrock with full conversation history + system prompt + compliance text
6. Parse for `UPDATE_FIELD:` signal at end of response
7. Save conversation history + config update to DynamoDB
8. Return `{response, configUpdate}`

### Bedrock System Message

```
You are a cloud security advisor for a {industry} company
configuring AWS {service}.

Company context:
  Compliance: {frameworks} ({maturity})
  Cost pressure: {costPressure}/5
  Risk tolerance: {riskTolerance}/5
  Security weight: {security} — never compromise this

Compliance reference:
{compliance_text}

The user has already seen this inline explanation:
{inlineReason}

Rules:
1. Do not repeat the inline reason — go deeper or address their concern
2. Tie response to THIS company's specific context
3. LOCKED_SECURE field + user wants to relax → explain why not, suggest alternative
4. Valid reason + adjustable field → suggest best alternative
5. If recommending change, end with:
   UPDATE_FIELD: {"fieldId": "...", "newValue": "...", "newReason": "..."}
6. No change needed → do not include UPDATE_FIELD
7. Keep responses to 3-4 sentences max
8. Never give generic advice
```

### UPDATE_FIELD Parsing

```python
if "UPDATE_FIELD:" in response:
    display_text = response.split("UPDATE_FIELD:")[0].strip()
    update_json = json.loads(response.split("UPDATE_FIELD:")[1].strip())
    config_update = {
        "fieldId": update_json["fieldId"],
        "newValue": update_json["newValue"],
        "newReason": update_json["newReason"]
    }
else:
    display_text = response
    config_update = None
```

---

## Task 6: [main.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/main.py) — FastAPI + Mangum

### Local Dev

```python
# uvicorn main:app --reload --port 5000
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
app.include_router(intent_router)
app.include_router(schema_router)
app.include_router(config_router)
app.include_router(explain_router)
```

### Lambda Deployment

```python
from mangum import Mangum
handler = Mangum(app)
# API Gateway invokes `handler` — Mangum translates APIGW events ↔ FastAPI
```

### Routes

| Method | Path | Router |
|--------|------|--------|
| POST | `/intent` | [routers/intent.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/routers/intent.py) |
| POST | `/schema` | [routers/schema.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/routers/schema.py) |
| POST | `/config` | [routers/config.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/routers/config.py) |
| POST | `/explain` | [routers/explain.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/routers/explain.py) |
| POST | `/terraform` | [routers/terraform.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/routers/terraform.py) (stretch) |

---

## Build Order

| Priority | File | Dependencies | Time Estimate |
|----------|------|-------------|---------------|
| 1 | [services/weights_engine.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/weights_engine.py) | None | 15 min |
| 2 | [services/field_classifier.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/field_classifier.py) | None | 15 min |
| 3 | [utils/bedrock_client.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/utils/bedrock_client.py) | boto3 | 15 min |
| 4 | [utils/dynamo_client.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/utils/dynamo_client.py) | boto3 | 10 min |
| 5 | [utils/s3_client.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/utils/s3_client.py) | boto3 | 10 min |
| 6 | [utils/compliance_mapper.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/utils/compliance_mapper.py) | s3_client | 10 min |
| 7 | `models/*.py` | pydantic | 15 min |
| 8 | [services/intent_service.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/intent_service.py) | bedrock, dynamo, weights_engine | 30 min |
| 9 | [services/config_service.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/config_service.py) | bedrock, dynamo, s3, compliance_mapper | 30 min |
| 10 | [services/explain_service.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/services/explain_service.py) | bedrock, dynamo, s3, compliance_mapper | 30 min |
| 11 | `routers/*.py` | models, services | 15 min |
| 12 | [main.py](file:///Users/hafizmohammedaahil/Documents/Hackathons/NIMBUS1000/Code/backend/main.py) | routers | 10 min |

**Total estimate: ~3.5 hours** → fits within hour 4 goal.

---

## Testing Commands

```bash
# Start local server
cd backend
uvicorn main:app --reload --port 5000

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
