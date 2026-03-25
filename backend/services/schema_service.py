import json
import logging
import os

from fastapi import HTTPException

from config import settings
from services.field_classifier import classify_field
from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import get_session
from utils.mcp_client import fetch_service_docs
from utils.s3_client import get_json, put_json
from utils.service_mapper import (
    get_mcp_query,
    get_provider_service_name,
    normalize_provider,
    slugify_service_name,
)

logger = logging.getLogger(__name__)

SCHEMA_PROMPT = """
You are building a machine-readable cloud configuration schema from provider documentation.

Provider: {provider}
Service: {service}

Documentation:
{documentation}

Return ONLY valid JSON in this exact shape:
{{
  "provider": "{provider}",
  "service": "{service}",
  "fields": [
    {{
      "fieldId": "exact provider API or Terraform field name",
      "label": "Human readable label",
      "type": "boolean|string|select|integer",
      "options": ["array if select type, else null"],
      "required": true,
      "securityRelevance": "critical|high|medium|low|none",
      "costRelevance": "high|medium|low|none",
      "complianceRelevance": ["HIPAA", "PCI-DSS", "SOC2"],
      "aiExplainable": true
    }}
  ]
}}

Rules:
- Include 6 to 12 fields most relevant to security, compliance, access, encryption, network exposure, auditing, and cost.
- Prefer exact field identifiers from the documentation.
- Use select with options only when the docs clearly imply finite values.
- Use empty arrays for complianceRelevance when unclear.
- Return JSON only with no prose or markdown fences.
"""


def validate_schema(schema: dict) -> dict:
    schema["provider"] = normalize_provider(schema.get("provider", "aws"))
    schema["service"] = schema.get("service", "")
    for field in schema.get("fields", []):
        if "securityRelevance" not in field:
            field["securityRelevance"] = "medium"
        if "complianceRelevance" not in field:
            field["complianceRelevance"] = []
        if "aiExplainable" not in field:
            field["aiExplainable"] = field["securityRelevance"] in ["critical", "high"]
        if "costRelevance" not in field:
            field["costRelevance"] = "none"
        if "options" not in field:
            field["options"] = None
        if "required" not in field:
            field["required"] = False
        if "type" not in field:
            field["type"] = "string"
        if "label" not in field:
            field["label"] = field.get("fieldId", "Field")
    return schema


def _schema_key(provider: str, service: str) -> str:
    return f"schemas/{normalize_provider(provider)}/{slugify_service_name(service)}.json"


def _load_local_schema(provider: str, service: str) -> dict | None:
    path = os.path.join(
        settings.SCHEMAS_DIR,
        normalize_provider(provider),
        f"{slugify_service_name(service)}.json",
    )
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _classify_schema(schema: dict, session_id: str) -> dict:
    session = get_session(session_id)
    weights = session.get("computedWeights", {})
    profile = session.get("companyProfile", {})
    active_frameworks = profile.get("complianceFrameworks", [])
    maturity = profile.get("complianceMaturity", "not-started")
    schema = validate_schema(schema)
    schema["fields"] = sorted(
        [
            classify_field(field, weights, active_frameworks, maturity)
            for field in schema.get("fields", [])
        ],
        key=lambda item: item.get("effectivePriority", 0),
        reverse=True,
    )
    return schema


def _generate_schema_from_docs(provider: str, service: str, docs: str) -> dict:
    prompt = SCHEMA_PROMPT.format(provider=provider, service=service, documentation=docs[:18000])
    schema = invoke_bedrock_json(prompt)
    schema["provider"] = normalize_provider(provider)
    schema["service"] = service
    return validate_schema(schema)


async def get_schema(service: str, provider: str = "aws", session_id: str | None = None) -> dict:
    provider = normalize_provider(provider)
    if provider not in settings.SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported.")

    canonical_service = get_provider_service_name(service, provider)
    cache_key = _schema_key(provider, canonical_service)
    schema = None

    try:
        schema = _load_local_schema(provider, canonical_service)
    except Exception as exc:
        logger.warning("Failed loading local schema for %s/%s: %s", provider, canonical_service, exc)

    if not schema:
        try:
            schema = get_json(settings.S3_BUCKET, cache_key)
        except Exception as exc:
            logger.warning("Failed loading cached schema from S3 for %s: %s", cache_key, exc)

    if not schema:
        try:
            docs = await fetch_service_docs(get_mcp_query(canonical_service, provider), provider=provider)
            if docs:
                schema = _generate_schema_from_docs(provider, canonical_service, docs)
                try:
                    put_json(settings.S3_BUCKET, cache_key, schema)
                except Exception as exc:
                    logger.warning("Failed to cache generated schema to S3 for %s: %s", cache_key, exc)
        except Exception as exc:
            logger.warning("Schema fetch via MCP failed for %s/%s: %s", provider, canonical_service, exc)

    if not schema:
        raise HTTPException(status_code=503, detail="Schema service temporarily unavailable.")

    schema["provider"] = provider
    schema["service"] = canonical_service
    if session_id:
        return _classify_schema(schema, session_id)
    return validate_schema(schema)
