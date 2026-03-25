import json
import logging

from fastapi import HTTPException

from utils.bedrock_client import invoke_bedrock
from utils.dynamo_client import get_service_provider, get_session, update_session
from utils.kb_client import get_compliance_context
from utils.service_mapper import get_provider_label

logger = logging.getLogger(__name__)

EXPLAIN_SYSTEM_PROMPT = """
You are a cloud security advisor for a {industry} company.

Company context:
- Compliance: {frameworks} ({maturity})
- Cost pressure: {costPressure}/5
- Risk tolerance: {riskTolerance}/5
- Security weight: {security_weight} (never compromise this)

Relevant compliance documentation:
{compliance_text}

Rules for all responses:
1. Do not repeat the inline reason - go deeper
2. Tie every response to THIS company's specific context
3. If field is LOCKED_SECURE and user wants to relax it:
   Explain why it cannot change, suggest alternatives
4. If user has valid reason and field is adjustable:
   Suggest best alternative and end with:
   UPDATE_FIELD: {"fieldId": "...", "newValue": "...", "newReason": "..."}
5. Keep responses to 3-4 sentences maximum
6. Never give generic advice - always company-specific
7. When explaining, quote specific clauses from documentation above
"""


def _find_service_for_field(session: dict, field_id: str) -> str | None:
    generated = session.get("generatedConfig", {})
    for service, config in generated.items():
        if field_id in config:
            return service
    return None


def _parse_update(response: str):
    if "UPDATE_FIELD:" not in response:
        return response.strip(), None
    display_text, update_text = response.split("UPDATE_FIELD:", 1)
    try:
        update = json.loads(update_text.strip())
        return display_text.strip(), {
            "fieldId": update["fieldId"],
            "newValue": update["newValue"],
            "newReason": update["newReason"],
        }
    except Exception:
        return response.strip(), None


def _deterministic_explanation(message: str, field_id: str, frameworks: list[str], current_value):
    lowered = message.lower()
    if field_id in {
        "ServerSideEncryptionConfiguration",
        "encryption.defaultKmsKeyName",
        "allowBlobPublicAccess",
    } and ("sse-s3" in lowered or "public" in lowered or "disable" in lowered):
        clause = "HIPAA \u00a7164.312(e)(2)(ii)" if "HIPAA" in frameworks else "security best practice"
        return (
            f"For this company, {current_value} should stay in place because {clause} favors stronger key control, "
            "restricted exposure, and auditability for sensitive records. The safer compromise is to tune cost on a "
            "less sensitive setting instead of relaxing a direct protection control."
        )
    return (
        "This setting was chosen to match your company's risk profile, compliance posture, and the specific "
        "service exposure involved. If you want to tune cost, we should do it on adjustable fields rather than "
        "weakening a control that carries direct security or audit impact."
    )


async def explain_field(
    session_id: str,
    field_id: str,
    field_label: str,
    current_value,
    inline_reason: str,
    message: str,
) -> dict:
    try:
        session = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")

    service = _find_service_for_field(session, field_id)
    if not service:
        raise HTTPException(status_code=400, detail=f"No config found for {field_id}. Generate config first.")

    profile = session.get("companyProfile", {})
    weights = session.get("computedWeights", {})
    frameworks = profile.get("complianceFrameworks", [])
    provider = get_service_provider(session_id, service) or session.get("provider", "aws")
    query = (
        f"{get_provider_label(provider)} {field_id} {field_label} compliance requirement "
        f"explanation why {current_value} may be wrong"
    )
    compliance_text = get_compliance_context(query=query, frameworks=frameworks, num_results=3)

    conversation_history = session.get("conversationHistory", {})
    service_history = conversation_history.setdefault(service, {})
    field_history = service_history.setdefault(field_id, [])
    if not field_history:
        field_history.append({"role": "assistant", "content": inline_reason})
    field_history.append({"role": "user", "content": message})

    system_prompt = EXPLAIN_SYSTEM_PROMPT
    replacements = {
        "{industry}": profile.get("industry", "other"),
        "{frameworks}": ", ".join(frameworks or ["none"]),
        "{maturity}": profile.get("complianceMaturity", "not-started"),
        "{costPressure}": str(profile.get("costPressure", 3)),
        "{riskTolerance}": str(profile.get("riskTolerance", 3)),
        "{security_weight}": str(weights.get("security", 0)),
        "{compliance_text}": compliance_text,
    }
    for key, value in replacements.items():
        system_prompt = system_prompt.replace(key, value)
    messages = [{"role": item["role"], "content": [{"text": item["content"]}]} for item in field_history]

    try:
        raw_response = invoke_bedrock(prompt="", system=system_prompt, messages=messages)
    except Exception as exc:
        logger.warning("Explain flow fell back to deterministic answer: %s", exc)
        raw_response = _deterministic_explanation(message, field_id, frameworks, current_value)

    response_text, config_update = _parse_update(raw_response)
    field_history.append({"role": "assistant", "content": response_text})

    if config_update:
        generated = session.get("generatedConfig", {})
        generated[service][field_id] = {
            "value": config_update["newValue"],
            "reason": config_update["newReason"],
        }
        update_session(session_id, "generatedConfig", generated)

    update_session(session_id, "conversationHistory", conversation_history)
    return {"response": response_text, "configUpdate": config_update}
