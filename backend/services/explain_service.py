# Explain / counter-ask service
# 1. Load session + conversation history from DynamoDB
# 2. Fetch matching compliance doc from S3
# 3. Seed context with inline reason if first message
# 4. Call Bedrock with full conversation history
# 5. Parse UPDATE_FIELD signal if present
# 6. Save updated history (+ config update) to DynamoDB
# 7. Return response + configUpdate

import json
import logging

from utils.bedrock_client import invoke_bedrock
from utils.dynamo_client import get_session, update_session
from utils.compliance_mapper import fetch_compliance_text

logger = logging.getLogger(__name__)

_EXPLAIN_SYSTEM = """\
You are a cloud security advisor for a {industry} company configuring AWS {service}.

Company context:
  Compliance: {frameworks} ({maturity})
  Cost pressure: {cost_pressure}/5
  Risk tolerance: {risk_tolerance}/5
  Security weight: {security} — never compromise this

Compliance reference:
{compliance_text}

The user has already seen this inline explanation:
{inline_reason}

Rules:
1. Do not repeat the inline reason — go deeper or address their concern
2. Tie response to THIS company's specific context
3. LOCKED_SECURE field + user wants to relax → explain why not, suggest alternative
4. Valid reason + adjustable field → suggest best alternative
5. If recommending change, end with:
   UPDATE_FIELD: {{"fieldId": "...", "newValue": "...", "newReason": "..."}}
6. No change needed → do not include UPDATE_FIELD
7. Keep responses to 3-4 sentences max
8. Never give generic advice
"""


def _parse_update_field(response: str) -> tuple[str, dict | None]:
    """
    Split Bedrock response into display text and optional config update.
    Returns (display_text, config_update_dict_or_None).
    """
    if "UPDATE_FIELD:" in response:
        parts = response.split("UPDATE_FIELD:", 1)
        display_text = parts[0].strip()
        try:
            update_json = json.loads(parts[1].strip())
            config_update = {
                "fieldId": update_json["fieldId"],
                "newValue": update_json["newValue"],
                "newReason": update_json["newReason"],
            }
            return display_text, config_update
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse UPDATE_FIELD: %s", e)
            return response, None
    return response, None


async def explain_field(
    session_id: str,
    field_id: str,
    field_label: str,
    current_value,
    inline_reason: str,
    message: str,
) -> dict:
    """
    Handle a conversational counter-ask about a single config field.
    Maintains per-field conversation history in DynamoDB.
    """
    # 1. Load session
    session = get_session(session_id)
    profile = session["companyProfile"]
    weights = {k: float(v) for k, v in session["computedWeights"].items()}
    service = session.get("selectedService", "unknown")
    conversation_history = session.get("conversationHistory", [])

    active_frameworks = profile.get("complianceFrameworks", [])
    maturity = profile.get("complianceMaturity", "not-started")

    # 2. Fetch compliance doc for this field
    compliance_text = fetch_compliance_text(
        active_frameworks,
        field={"fieldId": field_id, "label": field_label},
    )
    if not compliance_text:
        compliance_text = "(No matching compliance documents found)"

    # 3. Filter conversation history for this fieldId
    field_history = [
        msg for msg in conversation_history if msg.get("fieldId") == field_id
    ]

    # If no prior conversation for this field, seed with synthetic opening
    if not field_history:
        field_history.append({
            "role": "assistant",
            "content": inline_reason,
            "fieldId": field_id,
        })

    # 4. Append user message
    user_msg = {"role": "user", "content": message, "fieldId": field_id}
    field_history.append(user_msg)

    # 5. Build system prompt
    system = _EXPLAIN_SYSTEM.format(
        industry=profile.get("industry", "unknown"),
        service=service,
        frameworks=", ".join(active_frameworks) if active_frameworks else "none",
        maturity=maturity,
        cost_pressure=profile.get("costPressure", 3),
        risk_tolerance=profile.get("riskTolerance", 3),
        security=weights.get("security", 0),
        compliance_text=compliance_text,
        inline_reason=inline_reason,
    )

    # Build Bedrock messages (strip fieldId — Bedrock doesn't need it)
    bedrock_messages = [
        {
            "role": msg["role"],
            "content": [{"text": msg["content"]}],
        }
        for msg in field_history
    ]

    # 6. Call Bedrock (multi-turn mode — prompt unused when messages provided)
    raw_response = invoke_bedrock(
        prompt="",
        system=system,
        messages=bedrock_messages,
    )

    # 7. Parse UPDATE_FIELD signal
    display_text, config_update = _parse_update_field(raw_response)

    # 8. Append assistant response to history
    assistant_msg = {
        "role": "assistant",
        "content": display_text,
        "fieldId": field_id,
    }
    field_history.append(assistant_msg)

    # Merge field_history back into full conversation history
    # Remove old entries for this fieldId, then append new ones
    other_history = [
        msg for msg in conversation_history if msg.get("fieldId") != field_id
    ]
    updated_history = other_history + field_history

    # 9. Save to DynamoDB
    update_session(session_id, "conversationHistory", updated_history)

    # If there's a config update, also update the generated config
    if config_update:
        generated_config = session.get("generatedConfig", {})
        generated_config[config_update["fieldId"]] = {
            "value": config_update["newValue"],
            "reason": config_update["newReason"],
        }
        update_session(session_id, "generatedConfig", generated_config)
        logger.info(
            "Updated field %s to %s for session %s",
            config_update["fieldId"],
            config_update["newValue"],
            session_id,
        )

    return {
        "response": display_text,
        "configUpdate": config_update,
    }
