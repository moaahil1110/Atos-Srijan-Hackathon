import asyncio
import json

from fastapi import HTTPException

from services.schema_service import get_schema
from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import get_configured_services, get_session, save_service_config
from utils.grounding import (
    DEFAULT_RETRIEVAL_TOP_K,
    NIMBUS_SYSTEM_PROMPT,
    build_grounded_prompt,
    format_company_context,
    retrieve_decision_evidence,
)
from utils.service_mapper import get_provider_service_name, normalize_provider

CONFIG_OUTPUT_INSTRUCTION = """
Return ONLY valid JSON with one entry per fieldId from the schema.
Use this exact shape:
{
  "fieldId": {
    "value": <specific grounded value or null>,
    "reason": "Short explanation with a citation like [source#chunk]."
  }
}
Do not include markdown or extra commentary outside the JSON object.
""".strip()


def _weights(session: dict) -> dict:
    return session.get("weights") or session.get("computedWeights") or {}


def _sanitize_config(raw_config: dict, schema_fields: list[dict]) -> dict:
    allowed_fields = [field["fieldId"] for field in schema_fields]
    sanitized = {}
    for field_id in allowed_fields:
        entry = raw_config.get(field_id, {})
        if isinstance(entry, dict):
            sanitized[field_id] = {
                "value": entry.get("value"),
                "reason": entry.get("reason", "No grounded recommendation was produced for this field."),
            }
        else:
            sanitized[field_id] = {
                "value": entry,
                "reason": "No grounded recommendation was produced for this field.",
            }
    return sanitized


async def generate_config(session_id: str, service: str, provider: str = "aws") -> dict:
    provider = normalize_provider(provider)
    try:
        session = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")

    company_profile = session.get("companyProfile", {})
    weights = _weights(session)
    canonical_service = get_provider_service_name(service, provider)
    schema = await get_schema(service=canonical_service, provider=provider, session_id=session_id)
    schema_fields = schema.get("fields", [])
    field_names = [field["fieldId"] for field in schema_fields]

    evidence = retrieve_decision_evidence(
        company_profile=company_profile,
        provider=provider,
        service=canonical_service,
        field_names=field_names,
        top_k=DEFAULT_RETRIEVAL_TOP_K,
    )

    task_instruction = f"""
Recommend a grounded configuration for {canonical_service}.

Schema fields:
{json.dumps(schema_fields, indent=2, ensure_ascii=True)}

Rules:
- Return every fieldId exactly once.
- Use only the provider documentation and compliance chunks in this prompt.
- Include a short source citation in every reason using the retrieved source name and chunk number.
- If a field cannot be grounded from the retrieved evidence, set its value to null and say the documentation was insufficient.
""".strip()

    prompt = build_grounded_prompt(
        provider_chunks=evidence["provider"],
        company_context=format_company_context(provider, canonical_service, company_profile, weights),
        compliance_chunks=evidence["compliance"],
        task_instruction=task_instruction,
        output_instruction=CONFIG_OUTPUT_INSTRUCTION,
    )

    raw_config = await asyncio.to_thread(
        invoke_bedrock_json,
        prompt,
        system=NIMBUS_SYSTEM_PROMPT,
    )
    if not isinstance(raw_config, dict):
        raise HTTPException(status_code=502, detail="Nimbus returned an invalid configuration payload.")

    config = _sanitize_config(raw_config, schema_fields)
    save_service_config(
        session_id,
        canonical_service,
        config,
        provider=provider,
        decision_evidence=evidence,
    )
    return {
        "config": config,
        "service": canonical_service,
        "configuredServices": get_configured_services(session_id),
    }
