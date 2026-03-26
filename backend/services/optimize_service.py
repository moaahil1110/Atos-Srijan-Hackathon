import asyncio
import json

from fastapi import HTTPException

from services.schema_service import get_schema
from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import get_service_config, get_service_provider, get_session
from utils.kb_client import get_compliance_context
from utils.service_mapper import get_provider_label, get_provider_service_name

OPTIMIZE_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a cloud security auditor specialising in compliance gap analysis. Compare an existing cloud configuration against a recommended secure baseline and return ONLY a valid JSON array. No markdown, no explanation, no text outside the JSON array.
<|eot_id|><|start_header_id|>user<|end_header_id|>

Audit {provider} {service} for this company:

Company profile:
- Industry: {industry}
- Compliance frameworks: {frameworks} (maturity: {maturity})
- Risk tolerance: {riskTolerance}/5 (1 = very risk averse)
- Priority weights - security: {security}, compliance: {compliance}, cost: {cost}

Compliance documentation (cite specific clause numbers - never invent them):
{compliance_text}

EXISTING configuration (what the company currently has):
{existing_config_json}

RECOMMENDED configuration (NIMBUS1000 secure baseline):
{recommended_config_json}

For each field where EXISTING differs from RECOMMENDED, create one gap entry.

Severity rules:
- "critical": LOCKED_SECURE fields, direct compliance violations, or missing security controls
- "high": PREFER_SECURE fields weaker than recommended, significant security risk
- "medium": BALANCED/OPTIMISE_COST fields misconfigured, moderate risk
- "low": Minor deviations with minimal impact

Reason format:
- GOOD: "Violates HIPAA Section 164.312(e)(2)(ii): current value disables encryption of ePHI - SSE-KMS satisfies this clause and provides the audit trail required for your in-progress programme."
- BAD: "This value is weaker than recommended."
- If no clause applies: "Security best practice - current value increases attack surface by [specific risk]."

Treat any missing field as the most insecure possible default.
Sort results: critical first, then high, medium, low.
If there are no gaps, return: []

Return ONLY this JSON array:
[
  {{
    "fieldId": "exact field name from the config",
    "currentValue": "what the company currently has (as string)",
    "recommendedValue": "what it should be (as string)",
    "severity": "critical|high|medium|low",
    "reason": "compliance clause citation and specific security impact"
  }}
]
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
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


async def optimize_config(session_id: str, service: str, existing_config: dict) -> list:
    try:
        session = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")

    provider = get_service_provider(session_id, service) or session.get("provider", "aws")
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
        "{provider}": get_provider_label(provider),
        "{service}": canonical_service,
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

    response = await asyncio.to_thread(invoke_bedrock_json, prompt)
    gaps = response.get("gaps", response) if isinstance(response, dict) else response
    if not isinstance(gaps, list):
        gaps = []

    gaps = sorted(gaps, key=lambda item: SEVERITY_ORDER.get(str(item.get("severity", "low")).lower(), 4))
    for gap in gaps:
        gap["currentValue"] = str(gap.get("currentValue", ""))
        gap["recommendedValue"] = str(gap.get("recommendedValue", ""))
    return gaps
