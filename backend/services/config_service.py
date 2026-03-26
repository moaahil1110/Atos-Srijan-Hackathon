import asyncio
import json

from fastapi import HTTPException

from services.schema_service import get_schema
from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import get_configured_services, get_session, save_service_config
from utils.kb_client import get_compliance_context
from utils.service_mapper import get_provider_label, get_provider_service_name, normalize_provider

CONFIG_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a cloud security configuration expert for regulated industries. Your job is to choose the correct value for each configuration field and explain WHY using specific compliance clause numbers from the documentation provided. Return ONLY valid JSON - no markdown, no explanation, no text before or after the JSON.
<|eot_id|><|start_header_id|>user<|end_header_id|>

Configure {provider} {service} for this company:

Company profile:
- Industry: {industry}
- Compliance frameworks: {frameworks} (maturity: {maturity})
- Cost pressure: {costPressure}/5 (5 = very cost sensitive)
- Risk tolerance: {riskTolerance}/5 (1 = very risk averse)

Priority weights (non-negotiable, computed by backend):
- Security weight: {security_weight}
- Compliance weight: {compliance_weight}
- Cost weight: {cost_weight}

Compliance documentation (cite specific clause numbers - never invent them):
{compliance_text}

Fields to configure:
{fields_json}

Instruction tag rules - follow exactly:
- LOCKED_SECURE: Always the most secure value. Never relax for any reason including cost.
- PREFER_SECURE: Strongly prefer secure value. May briefly note cost trade-off.
- OPTIMISE_COST: A cost-efficient option is acceptable here.
- BALANCED: Use judgement based on the company profile.

Citation rules:
- GOOD reason: "HIPAA Section 164.312(e)(2)(ii) requires encryption of ePHI in transit - SSE-KMS satisfies this and provides the audit trail needed for your in-progress HIPAA programme."
- BAD reason: "Encryption is important for security."
- If no specific clause applies: "Security best practice - [brief one-line rationale]."

Return ONLY this JSON object (one entry per fieldId, exactly two keys each):
{
  "fieldId_example": {"value": <the recommended value>, "reason": "<clause citation and explanation>"}
}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""


async def generate_config(session_id: str, service: str, provider: str = "aws") -> dict:
    provider = normalize_provider(provider)
    try:
        session = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")

    intent = session.get("companyProfile", {})
    weights = session.get("computedWeights", {})
    canonical_service = get_provider_service_name(service, provider)
    schema = await get_schema(service=canonical_service, provider=provider, session_id=session_id)
    schema_fields = schema.get("fields", [])

    security_fields = [
        field["fieldId"] for field in schema_fields if field.get("securityRelevance") in ["critical", "high"]
    ]
    compliance_query = (
        f"{get_provider_label(provider)} {canonical_service} security configuration "
        f"requirements for {', '.join(security_fields[:5])}"
    )
    compliance_text = get_compliance_context(
        query=compliance_query,
        frameworks=intent.get("complianceFrameworks", []),
        num_results=5,
    )

    prompt = CONFIG_PROMPT
    replacements = {
        "{provider}": get_provider_label(provider),
        "{service}": canonical_service,
        "{industry}": intent.get("industry", "other"),
        "{frameworks}": ", ".join(intent.get("complianceFrameworks", ["none"])),
        "{maturity}": intent.get("complianceMaturity", "not-started"),
        "{costPressure}": str(intent.get("costPressure", 3)),
        "{riskTolerance}": str(intent.get("riskTolerance", 3)),
        "{security_weight}": str(weights.get("security", 0)),
        "{compliance_weight}": str(weights.get("compliance", 0)),
        "{cost_weight}": str(weights.get("cost", 0)),
        "{compliance_text}": compliance_text,
        "{fields_json}": json.dumps(schema_fields, indent=2),
    }
    for key, value in replacements.items():
        prompt = prompt.replace(key, value)

    config = await asyncio.to_thread(invoke_bedrock_json, prompt)

    save_service_config(session_id, canonical_service, config, provider=provider)
    return {
        "config": config,
        "service": canonical_service,
        "configuredServices": get_configured_services(session_id),
    }
