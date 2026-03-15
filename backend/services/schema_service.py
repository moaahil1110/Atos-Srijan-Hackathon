# Schema fetch service
# 1. Check local / S3 cache for schemas/aws/{service}.json
# 2. If miss: generate schema via Bedrock
# 3. Run field_classifier on every field
# 4. Cache to S3
# 5. Return classified schema

import json
import os
import logging

from config import settings
from utils.dynamo_client import get_session
from utils.s3_client import get_json, put_json
from utils.bedrock_client import invoke_bedrock_json
from services.field_classifier import classify_field

logger = logging.getLogger(__name__)

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


async def get_schema(
    service: str,
    provider: str,
    session_id: str,
) -> dict:
    """
    Load the schema for a given service.
    Strategy:
      1. Local JSON file (fastest)
      2. S3 cache bucket
      3. Generation via Bedrock AI (fallback)
    Then runs field_classifier to enrich fields with weights.
    """
    schema = None
    cache_key = f"schemas/{provider}/{service.lower()}.json"

    # 1. Try Local JSON file
    schema_path = os.path.join(settings.SCHEMAS_DIR, provider, f"{service.lower()}.json")
    if os.path.exists(schema_path):
        try:
            with open(schema_path, "r") as f:
                schema = json.load(f)
                logger.info("Loaded schema from local disk: %s", schema_path)
        except Exception as e:
            logger.warning("Failed to read local schema %s: %s", schema_path, e)

    # 2. Try S3 Cache (if local miss)
    if not schema or not schema.get("fields"):
        try:
            schema = get_json(settings.SCHEMA_BUCKET, cache_key)
            if schema:
                logger.info("Loaded schema from S3 cache: %s", cache_key)
        except Exception as e:
            logger.warning("Failed to read S3 cache for schema %s: %s", cache_key, e)

    # 3. Fallback: Generate via Bedrock
    if not schema or not schema.get("fields"):
        logger.info("Schema miss for %s. Generating via Bedrock...", service)
        prompt = (
            f"{SCHEMA_STRUCTURING_PROMPT}\n\n"
            f"Extract all configuration fields for {service.upper()}. "
            f"Focus on security, compliance, and cost-relevant parameters."
        )
        try:
            schema = invoke_bedrock_json(prompt)
            logger.info("Generated schema via Bedrock for %s", service)
            
            # Cache the newly generated schema into S3 for next time
            try:
                put_json(settings.SCHEMA_BUCKET, cache_key, schema)
                logger.info("Cached generated schema to S3: %s", cache_key)
            except Exception as e:
                 logger.warning("Failed to write schema to S3 cache: %s", e)
                 
        except Exception as e:
            logger.error("Failed to generate schema via Bedrock for %s: %s", service, e)
            raise ValueError(f"Could not load or generate schema for {service}")

    # 4. Load session for weights
    session = get_session(session_id)
    weights = {k: float(v) for k, v in session["computedWeights"].items()}
    profile = session["companyProfile"]
    active_frameworks = profile.get("complianceFrameworks", [])
    maturity = profile.get("complianceMaturity", "not-started")

    # 5. Classify each field
    raw_fields = schema.get("fields", [])
    classified_fields = [
        classify_field(f, weights, active_frameworks, maturity)
        for f in raw_fields
    ]

    # Sort by effectivePriority descending (Person 2's addition)
    classified_fields.sort(key=lambda f: f.get("effectivePriority", 0), reverse=True)

    schema["fields"] = classified_fields

    logger.info(
        "Loaded schema %s/%s — %d fields classified",
        provider, service, len(classified_fields),
    )

    return schema
