import asyncio
import json
import logging

from fastapi import HTTPException

from services.schema_service import get_schema
from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import get_service_config, get_session
from utils.kb_client import get_compliance_context
from utils.service_mapper import (
    get_provider_label,
    get_provider_service_name,
)

logger = logging.getLogger(__name__)

OPTIMIZE_PROMPT = """
You are a cloud security auditor for a {industry} company.

Company profile:
- Compliance: {frameworks} ({maturity})
- Risk tolerance: {riskTolerance}/5
- Priority weights: security={security}, compliance={compliance}, cost={cost}

Compliance documentation:
{compliance_text}

Compare EXISTING configuration against RECOMMENDED configuration.

EXISTING (what the company currently has):
{existing_config_json}

RECOMMENDED (what NIMBUS1000 generated):
{recommended_config_json}

For each field where existing differs from recommended,
create a gap entry.

Rules:
- LOCKED_SECURE fields: severity is always "critical"
- Compliance violations: severity is "critical"
- Missing fields: treat as most insecure default
- Reasons must cite: "Violates {FRAMEWORK} \u00a7{CLAUSE}: explanation"
- If no clause applies, use security impact for severity

Return ONLY a valid JSON array sorted critical first:
[
  {
    "fieldId": "exact field name",
    "currentValue": "what user has",
    "recommendedValue": "what it should be",
    "severity": "critical|high|medium|low",
    "reason": "Violates HIPAA \u00a7164.312(e)(2)(ii): ..."
  }
]
"""

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _default_insecure_value(field: dict):
    field_type = field.get("type")
    if field_type == "boolean":
        return False
    if field_type == "select":
        return "None"
    if field_type == "integer":
        return 0
    return ""


def _normalize_recommended_value(entry):
    if isinstance(entry, dict) and "value" in entry:
        return entry["value"], entry.get("reason", "")
    return entry, ""


def _severity(field: dict) -> str:
    if field.get("instruction") == "LOCKED_SECURE":
        return "critical"
    if field.get("complianceActive"):
        return "critical"
    if field.get("securityRelevance") == "high":
        return "high"
    if field.get("securityRelevance") == "medium":
        return "medium"
    return "low"


def _deterministic_gaps(schema_fields: list[dict], existing_config: dict, recommended_config: dict, frameworks: list[str]):
    gaps = []
    clause = "HIPAA \u00a7164.312(e)(2)(ii)" if "HIPAA" in frameworks else "security best practice"
    for field in schema_fields:
        recommended_value, recommended_reason = _normalize_recommended_value(recommended_config.get(field["fieldId"]))
        existing_value = existing_config.get(field["fieldId"], _default_insecure_value(field))
        if str(existing_value) == str(recommended_value):
            continue
        severity = _severity(field)
        reason_prefix = f"Violates {clause}: " if "HIPAA" in frameworks else ""
        fallback_reason = f"{field['label']} is weaker than the recommended secure baseline."
        gaps.append(
            {
                "fieldId": field["fieldId"],
                "currentValue": str(existing_value),
                "recommendedValue": str(recommended_value),
                "severity": severity,
                "reason": f"{reason_prefix}{recommended_reason or fallback_reason}",
            }
        )
    return sorted(gaps, key=lambda item: SEVERITY_ORDER.get(item["severity"], 4))


async def optimize_config(session_id: str, service: str, existing_config: dict) -> list:
    try:
        session = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")

    provider = session.get("provider", "aws")
    canonical_service = get_provider_service_name(service, provider)
    recommended_config = get_service_config(session_id, canonical_service)
    if not recommended_config:
        raise HTTPException(
            status_code=400,
            detail=f"No config found for {canonical_service}. Generate config first.",
        )

    schema = await get_schema(service=canonical_service, provider=provider, session_id=session_id)
    padded_existing = {}
    for field in schema.get("fields", []):
        padded_existing[field["fieldId"]] = existing_config.get(field["fieldId"], _default_insecure_value(field))

    profile = session.get("companyProfile", {})
    weights = session.get("computedWeights", {})
    frameworks = profile.get("complianceFrameworks", [])
    query = (
        f"{get_provider_label(provider)} {canonical_service} security gaps misconfiguration risks for "
        f"{', '.join(list(padded_existing.keys())[:5])}"
    )
    compliance_text = get_compliance_context(query=query, frameworks=frameworks, num_results=5)
    prompt = OPTIMIZE_PROMPT
    replacements = {
        "{industry}": profile.get("industry", "other"),
        "{frameworks}": ", ".join(frameworks or ["none"]),
        "{maturity}": profile.get("complianceMaturity", "not-started"),
        "{riskTolerance}": str(profile.get("riskTolerance", 3)),
        "{security}": str(weights.get("security", 0)),
        "{compliance}": str(weights.get("compliance", 0)),
        "{cost}": str(weights.get("cost", 0)),
        "{compliance_text}": compliance_text,
        "{existing_config_json}": json.dumps(padded_existing, indent=2),
        "{recommended_config_json}": json.dumps(recommended_config, indent=2),
    }
    for key, value in replacements.items():
        prompt = prompt.replace(key, value)

    try:
        response = await asyncio.to_thread(invoke_bedrock_json, prompt)
        gaps = response.get("gaps", response if isinstance(response, list) else [])
    except Exception as exc:
        logger.warning("Optimize flow fell back to deterministic comparison: %s", exc)
        gaps = _deterministic_gaps(schema.get("fields", []), padded_existing, recommended_config, frameworks)

    gaps = sorted(gaps, key=lambda item: SEVERITY_ORDER.get(str(item.get("severity", "low")).lower(), 4))
    for gap in gaps:
        gap["currentValue"] = str(gap.get("currentValue", ""))
        gap["recommendedValue"] = str(gap.get("recommendedValue", ""))
    return gaps
