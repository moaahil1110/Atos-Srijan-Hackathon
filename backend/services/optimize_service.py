import asyncio
import json

from fastapi import HTTPException

from services.schema_service import get_schema
from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import (
    get_service_config,
    get_service_provider,
    get_session,
    update_session_fields,
)
from utils.grounding import (
    DEFAULT_RETRIEVAL_TOP_K,
    NIMBUS_SYSTEM_PROMPT,
    build_grounded_prompt,
    format_company_context,
    retrieve_decision_evidence,
)
from utils.service_mapper import get_provider_service_name

OPTIMIZE_OUTPUT_INSTRUCTION = """
Return ONLY a valid JSON array.
Each entry must follow this shape:
[
  {
    "fieldId": "field name",
    "currentValue": "current value as text",
    "recommendedValue": "recommended value as text",
    "severity": "critical|high|medium|low",
    "reason": "Grounded explanation with a citation like [source#chunk]."
  }
]
Return [] when there are no grounded gaps.
""".strip()

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _weights(session: dict) -> dict:
    return session.get("weights") or session.get("computedWeights") or {}


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

    provider = get_service_provider(session_id, service) or session.get("selectedProvider") or session.get("provider", "aws")
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

    company_profile = session.get("companyProfile", {})
    weights = _weights(session)
    evidence = retrieve_decision_evidence(
        company_profile=company_profile,
        provider=provider,
        service=canonical_service,
        field_names=[field["fieldId"] for field in schema.get("fields", [])],
        current_config=padded_existing,
        top_k=DEFAULT_RETRIEVAL_TOP_K,
    )

    task_instruction = f"""
Compare the current configuration for {canonical_service} against Nimbus's generated configuration.

Recommended configuration:
{json.dumps(recommended_config, indent=2, ensure_ascii=True)}

Rules:
- Only report differences that are grounded in the retrieved provider or compliance evidence.
- Treat any missing current field as the most insecure practical default.
- If a difference is not grounded by the retrieved evidence, do not include it.
- Sort the final list by severity from critical to low.
""".strip()

    prompt = build_grounded_prompt(
        provider_chunks=evidence["provider"],
        company_context=format_company_context(provider, canonical_service, company_profile, weights),
        compliance_chunks=evidence["compliance"],
        current_config=padded_existing,
        task_instruction=task_instruction,
        output_instruction=OPTIMIZE_OUTPUT_INSTRUCTION,
    )

    response = await asyncio.to_thread(
        invoke_bedrock_json,
        prompt,
        system=NIMBUS_SYSTEM_PROMPT,
    )
    gaps = response.get("gaps", response) if isinstance(response, dict) else response
    if not isinstance(gaps, list):
        gaps = []

    gaps = sorted(gaps, key=lambda item: SEVERITY_ORDER.get(str(item.get("severity", "low")).lower(), 4))
    for gap in gaps:
        gap["currentValue"] = str(gap.get("currentValue", ""))
        gap["recommendedValue"] = str(gap.get("recommendedValue", ""))

    decision_evidence_by_service = session.get("decisionEvidenceByService", {})
    decision_evidence_by_service[canonical_service] = evidence
    update_session_fields(
        session_id,
        {
            "currentConfig": padded_existing,
            "selectedProvider": provider,
            "selectedService": canonical_service,
            "decisionEvidence": evidence,
            "decisionEvidenceByService": decision_evidence_by_service,
        },
    )
    return gaps
