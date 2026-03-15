#!/bin/bash
# NIMBUS1000 — FastAPI Backend Setup
# Run from your project root: bash setup_project.sh

echo "Setting up NIMBUS1000 FastAPI backend..."

# ── Dirs ──────────────────────────────────────────────────────
mkdir -p backend/routers
mkdir -p backend/services
mkdir -p backend/models
mkdir -p backend/utils
mkdir -p compliance-docs
mkdir -p schemas/aws
mkdir -p docs

# ── .python-version ───────────────────────────────────────────
echo "3.11" > backend/.python-version

# ── requirements.txt ──────────────────────────────────────────
cat > backend/requirements.txt << 'EOF'
fastapi
uvicorn[standard]
boto3
python-dotenv
pydantic
mangum
EOF

# ── .env ──────────────────────────────────────────────────────
cat > backend/.env << 'EOF'
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=ap-south-1
DYNAMODB_TABLE=CopilotSessions
SCHEMA_BUCKET=cloud-copilot-schemas
COMPLIANCE_BUCKET=cloud-copilot-compliance-docs
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
EOF

# ── main.py ───────────────────────────────────────────────────
cat > backend/main.py << 'EOF'
# main.py — FastAPI entry point
# Local dev: uvicorn main:app --reload --port 5000
# Lambda:    handler = Mangum(app)
EOF

# ── config.py ─────────────────────────────────────────────────
cat > backend/config.py << 'EOF'
# config.py — loads .env vars into a settings object
EOF

# ── __init__.py files ─────────────────────────────────────────
touch backend/__init__.py
touch backend/routers/__init__.py
touch backend/services/__init__.py
touch backend/models/__init__.py
touch backend/utils/__init__.py

# ── Routers (one per API route) ───────────────────────────────
cat > backend/routers/intent.py << 'EOF'
# POST /intent
# Calls: services/intent_service.py
EOF

cat > backend/routers/schema.py << 'EOF'
# POST /schema
# Calls: services/schema_service.py
EOF

cat > backend/routers/config.py << 'EOF'
# POST /config
# Calls: services/config_service.py
EOF

cat > backend/routers/explain.py << 'EOF'
# POST /explain
# Calls: services/explain_service.py
EOF

cat > backend/routers/terraform.py << 'EOF'
# POST /terraform  (stretch goal)
# Calls: services/terraform_service.py
EOF

# ── Services (business logic) ─────────────────────────────────
cat > backend/services/intent_service.py << 'EOF'
# Intent extraction service
# 1. Call Bedrock to extract structured profile from description
# 2. Call weights_engine.compute_weights()
# 3. Save session to DynamoDB
# 4. Return sessionId + intent + weights
EOF

cat > backend/services/schema_service.py << 'EOF'
# Schema fetch service
# 1. Check S3 cache for schemas/aws/{service}.json
# 2. If miss: fetch via MCP server
# 3. Run field_classifier on every field
# 4. Cache result to S3
# 5. Return classified schema
EOF

cat > backend/services/config_service.py << 'EOF'
# Config generation service
# 1. Load session from DynamoDB
# 2. Fetch relevant compliance docs from S3
# 3. Build prompt with weights + fields + compliance text
# 4. Call Bedrock — every field gets value + reason
# 5. Save config to DynamoDB
# 6. Return config map
EOF

cat > backend/services/explain_service.py << 'EOF'
# Explain / counter-ask service
# 1. Load session + conversation history from DynamoDB
# 2. Fetch matching compliance doc from S3
# 3. Seed context with inline reason if first message
# 4. Call Bedrock with full conversation history
# 5. Parse UPDATE_FIELD signal if present
# 6. Save updated history (+ config update) to DynamoDB
# 7. Return response + configUpdate
EOF

cat > backend/services/terraform_service.py << 'EOF'
# Terraform export service  (stretch goal — attempt hour 8)
# 1. Load session config from DynamoDB
# 2. Extract values only (drop reasons)
# 3. Call Bedrock to generate .tf file
# 4. Return terraform content string
EOF

# ── Core logic modules ────────────────────────────────────────
cat > backend/services/weights_engine.py << 'EOF'
# Pure Python — zero AWS dependencies
# compute_weights(intent: dict) -> {"security": float, "compliance": float, "cost": float}
# All three values always sum to exactly 1.0
# Person 1 owns this file
EOF

cat > backend/services/field_classifier.py << 'EOF'
# Pure Python — zero AWS dependencies
# classify_field(field, weights, active_frameworks, maturity) -> field with added keys:
#   instruction: LOCKED_SECURE | PREFER_SECURE | OPTIMISE_COST | BALANCED
#   effectivePriority: float
#   complianceActive: bool
# Person 1 owns this file
EOF

# ── Models (Pydantic schemas) ─────────────────────────────────
cat > backend/models/intent.py << 'EOF'
# Pydantic models for /intent
# IntentRequest  — { description: str }
# IntentResponse — { sessionId, intent, weights }
EOF

cat > backend/models/schema.py << 'EOF'
# Pydantic models for /schema
# SchemaRequest  — { service, provider, sessionId }
# SchemaResponse — { schema: { provider, service, fields[] } }
EOF

cat > backend/models/config.py << 'EOF'
# Pydantic models for /config
# ConfigRequest  — { sessionId, schema, service }
# ConfigResponse — { config: { fieldId: { value, reason } } }
EOF

cat > backend/models/explain.py << 'EOF'
# Pydantic models for /explain
# ExplainRequest  — { sessionId, fieldId, fieldLabel, currentValue, inlineReason, message }
# ExplainResponse — { response: str, configUpdate: null | { fieldId, newValue, newReason } }
EOF

# ── Utils ─────────────────────────────────────────────────────
cat > backend/utils/bedrock_client.py << 'EOF'
# Shared boto3 Bedrock client
# Call bedrock using converse() API
# Handles JSON parsing + retry on malformed response
EOF

cat > backend/utils/dynamo_client.py << 'EOF'
# Shared DynamoDB helper
# get_session(session_id) -> dict
# save_session(item) -> None
# update_session(session_id, key, value) -> None
EOF

cat > backend/utils/s3_client.py << 'EOF'
# Shared S3 helper
# get_object(bucket, key) -> str
# put_object(bucket, key, body) -> None
EOF

cat > backend/utils/compliance_mapper.py << 'EOF'
# Maps (framework, field_type) -> S3 compliance doc path
# fetch_compliance_text(field, active_frameworks) -> str
# Used by config_service and explain_service
EOF

# ── Compliance doc stubs ──────────────────────────────────────
for f in \
  hipaa-access-controls \
  hipaa-encryption \
  hipaa-logging \
  pcidss-access \
  pcidss-encryption \
  pcidss-logging \
  soc2-access \
  soc2-logging
do
  cat > compliance-docs/${f}.txt << EOF
# ${f}.txt
# TODO: paste actual clause text here
# Must include clause number e.g. HIPAA §164.312(e)(2)(ii)
EOF
done

# ── Pre-cached schema stubs ───────────────────────────────────
for svc in s3 rds iam; do
  cat > schemas/aws/${svc}.json << EOF
{
  "provider": "aws",
  "service": "${svc^^}",
  "fields": []
}
EOF
done

# ── .gitignore ────────────────────────────────────────────────
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
*.pyo
.venv/
venv/
node_modules/
.DS_Store
EOF

echo ""
echo "Done! Structure:"
find backend compliance-docs schemas -type f | sort