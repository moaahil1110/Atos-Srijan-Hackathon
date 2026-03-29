import json

from fastapi import HTTPException

from utils.bedrock_client import invoke_bedrock
from utils.dynamo_client import get_service_provider, get_session, update_session_fields
from utils.grounding import (
    DEFAULT_RETRIEVAL_TOP_K,
    NIMBUS_SYSTEM_PROMPT,
    build_grounded_prompt,
    format_company_context,
    retrieve_decision_evidence,
)

EXPLAIN_OUTPUT_INSTRUCTION = """
Respond in plain text only.
Keep the explanation concise and specific.
If the field should change, end with:
UPDATE_FIELD: {"fieldId":"...","newValue":"...","newReason":"..."}
Otherwise do not include UPDATE_FIELD.
""".strip()


def _weights(session: dict) -> dict:
    return session.get("weights") or session.get("computedWeights") or {}


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

    provider = get_service_provider(session_id, service) or session.get("selectedProvider") or session.get("provider", "aws")
    company_profile = session.get("companyProfile", {})
    weights = _weights(session)

    evidence = (session.get("decisionEvidenceByService", {}) or {}).get(service) or session.get("decisionEvidence")
    if not evidence or not evidence.get("provider") or not evidence.get("compliance"):
        evidence = retrieve_decision_evidence(
            company_profile=company_profile,
            provider=provider,
            service=service,
            field_names=[field_id, field_label],
            current_config=session.get("currentConfig") or {field_id: current_value},
            top_k=DEFAULT_RETRIEVAL_TOP_K,
        )

    field_history = session.get("fieldConversationHistory", {})
    service_history = field_history.setdefault(service, {})
    history = service_history.setdefault(field_id, [])
    if not history:
        history.append({"role": "assistant", "content": inline_reason})
    history.append({"role": "user", "content": message})

    task_instruction = f"""
Explain the decision for field '{field_id}' ({field_label}).

Current displayed value:
{current_value}

Existing inline reason:
{inline_reason}

Conversation history for this field:
{json.dumps(history, indent=2, ensure_ascii=True)}

Rules:
- Use the retrieved provider documentation first, then company context, then compliance evidence.
- Explain conflicts between provider defaults and compliance explicitly.
- If the user asks for a change and the evidence supports it, include a valid UPDATE_FIELD payload.
- If the evidence does not support a change, explain why and do not guess.
""".strip()

    prompt = build_grounded_prompt(
        provider_chunks=evidence.get("provider", []),
        company_context=format_company_context(provider, service, company_profile, weights),
        compliance_chunks=evidence.get("compliance", []),
        task_instruction=task_instruction,
        output_instruction=EXPLAIN_OUTPUT_INSTRUCTION,
    )

    raw_response = invoke_bedrock(prompt, system=NIMBUS_SYSTEM_PROMPT, max_tokens=500, temperature=0.2)
    response_text, config_update = _parse_update(raw_response)

    history.append({"role": "assistant", "content": response_text})

    updates = {
        "fieldConversationHistory": field_history,
        "selectedProvider": provider,
        "selectedService": service,
        "decisionEvidence": evidence,
    }

    evidence_by_service = session.get("decisionEvidenceByService", {})
    evidence_by_service[service] = evidence
    updates["decisionEvidenceByService"] = evidence_by_service

    conversation_history = session.get("conversationHistory", [])
    conversation_history.extend(
        [
            {"role": "user", "service": service, "fieldId": field_id, "content": message},
            {"role": "assistant", "service": service, "fieldId": field_id, "content": response_text},
        ]
    )
    updates["conversationHistory"] = conversation_history

    if config_update:
        generated = session.get("generatedConfig", {})
        generated.setdefault(service, {})
        generated[service][field_id] = {
            "value": config_update["newValue"],
            "reason": config_update["newReason"],
        }
        updates["generatedConfig"] = generated

    update_session_fields(session_id, updates)
    return {"response": response_text, "configUpdate": config_update}
