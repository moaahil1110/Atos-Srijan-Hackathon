"""Schema fetch service — Person 2 owns this.
1. Check S3 cache for schemas/aws/{service}.json
2. If miss: call Bedrock to generate schema from AWS docs knowledge
3. Run field_classifier on every field
4. Cache classified result to S3
5. Return classified schema
"""
import json
from utils.s3_client import get_json, put_json
from utils.dynamo_client import get_session
from utils.bedrock_client import call_bedrock_json
from services.field_classifier import classify_field
from config import SCHEMA_BUCKET

SCHEMA_STRUCTURING_PROMPT = """You are an AWS service configuration expert.
Extract ALL important configuration fields for the specified AWS service.
Return ONLY a JSON object with this exact structure:
{
  "provider": "aws",
  "service": "<SERVICE_NAME>",
  "fields": [
    {
      "fieldId": "exact AWS API parameter name",
      "label": "human readable label",
      "type": "boolean or string or select or integer",
      "options": ["array of allowed values if select, else null"],
      "required": true or false,
      "securityRelevance": "critical or high or medium or low or none",
      "costRelevance": "high or medium or low or none",
      "complianceRelevance": ["array of: HIPAA, PCI-DSS, SOC2, ISO27001"],
      "aiExplainable": true if wrong value creates security or cost risk else false
    }
  ]
}

Rules:
- fieldId must be the EXACT AWS API parameter name
- Include at least 8-12 fields covering security, cost, and compliance aspects
- securityRelevance "critical" = changing this field could directly cause a security breach
- Mark encryption, public access, MFA, and authentication fields as security critical
- Mark instance sizing, storage tiers, and replication as cost relevant
- complianceRelevance should list frameworks where the field is specifically mentioned
- Return ONLY the JSON, no explanation, no markdown fences"""


def fetch_schema(service: str, provider: str, session_id: str) -> dict:
    """Fetch and classify a service schema. Uses S3 cache when available."""

    # ── Step 1: Check S3 cache ─────────────────────────────────
    cache_key = f"schemas/{provider}/{service.lower()}.json"
    cached = get_json(SCHEMA_BUCKET, cache_key)

    if cached and cached.get("fields"):
        schema = cached
    else:
        # ── Step 2: Generate schema via Bedrock ────────────────
        schema = call_bedrock_json(
            SCHEMA_STRUCTURING_PROMPT,
            f"Extract all configuration fields for AWS {service}. "
            f"Focus on security, compliance, and cost-relevant parameters."
        )

    # ── Step 3: Get session for weights + frameworks ───────────
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    weights = session.get("computedWeights", {"security": 0.50, "compliance": 0.25, "cost": 0.25})
    profile = session.get("companyProfile", {})
    active_frameworks = profile.get("complianceFrameworks", [])
    maturity = profile.get("complianceMaturity", "not-started")

    # ── Step 4: Classify every field ───────────────────────────
    classified_fields = []
    for field in schema.get("fields", []):
        classified = classify_field(field, weights, active_frameworks, maturity)
        classified_fields.append(classified)

    # Sort by effectivePriority descending
    classified_fields.sort(key=lambda f: f.get("effectivePriority", 0), reverse=True)

    classified_schema = {
        "provider": schema.get("provider", provider),
        "service": schema.get("service", service),
        "fields": classified_fields,
    }

    # ── Step 5: Cache classified schema to S3 ──────────────────
    try:
        put_json(SCHEMA_BUCKET, cache_key, classified_schema)
    except Exception:
        pass  # Cache write failure is non-fatal

    return classified_schema
