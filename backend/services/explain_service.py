"""Explain / counter-ask service — Person 1 owns this.
1. Load session + conversation history from DynamoDB
2. Fetch matching compliance doc from S3
3. Seed context with inline reason if first message
4. Call Bedrock with full conversation history
5. Parse UPDATE_FIELD signal if present
6. Save updated history (+ config update) to DynamoDB
7. Return response + configUpdate
"""
import json
from utils.bedrock_client import call_bedrock_conversation
from utils.dynamo_client import get_session, update_session
from utils.compliance_mapper import fetch_compliance_text

EXPLAIN_SYSTEM_PROMPT = """You are a cloud security advisor for a {industry} company configuring AWS {service}.

Company context:
Compliance: {frameworks} ({maturity})
Cost pressure: {cost_pressure}/5
Risk tolerance: {risk_tolerance}/5
Security weight: {security} — never compromise this

Compliance reference:
{compliance_text}

The user has already seen this inline explanation:
"{inline_reason}"

They are now asking a follow-up question or pushing back.
Respond to their specific concern with full context.

Rules:
1. Do not repeat the inline reason — the user already read it. Go deeper or address their specific concern directly.
2. Always tie response to THIS company's specific context.
3. If field is LOCKED_SECURE and user wants to relax it, explain why it cannot change and suggest a safe alternative.
4. If user has a valid reason and field allows adjustment, suggest the best alternative.
5. If recommending a field value change, end your response with exactly this on its own line:
   UPDATE_FIELD: {{"fieldId": "...", "newValue": "...", "newReason": "..."}}
   newReason must be a one-sentence explanation of the new value.
6. If no change needed, do not include UPDATE_FIELD at all.
7. Keep responses to 3-4 sentences maximum.
8. Never give generic advice."""


def explain_field(session_id: str, field_id: str, field_label: str,
                  current_value, inline_reason: str, message: str) -> dict:
    """Handle follow-up questions and counter-asks on a specific field."""

    # ── Step 1: Load session ───────────────────────────────────
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    profile = session.get("companyProfile", {})
    weights = session.get("computedWeights", {})
    service = session.get("selectedService", "S3")
    config = session.get("generatedConfig", {})
    history = session.get("conversationHistory", [])

    active_frameworks = profile.get("complianceFrameworks", [])

    # ── Step 2: Fetch compliance doc ───────────────────────────
    # Build a synthetic field dict for the compliance mapper
    field_for_lookup = {
        "fieldId": field_id,
        "label": field_label,
        "complianceRelevance": [],
    }
    # Try to find the field's complianceRelevance from config context
    schema_fields = session.get("schemaFields", [])
    for sf in schema_fields:
        if sf.get("fieldId") == field_id:
            field_for_lookup = sf
            break

    compliance_text = fetch_compliance_text(field_for_lookup, active_frameworks)

    # ── Step 3: Seed context if first message for this field ───
    field_history = [m for m in history if m.get("fieldId") == field_id]
    if not field_history:
        # Seed with user context + assistant reason (Llama requires user-first)
        history.append({
            "role": "user",
            "content": f"You recommended {current_value} for {field_label}. Why?",
            "fieldId": field_id,
        })
        history.append({
            "role": "assistant",
            "content": inline_reason,
            "fieldId": field_id,
        })

    # ── Step 4: Append user message ────────────────────────────
    history.append({
        "role": "user",
        "content": message,
        "fieldId": field_id,
    })

    # ── Step 5: Call Bedrock with conversation ─────────────────
    system_prompt = EXPLAIN_SYSTEM_PROMPT.format(
        industry=profile.get("industry", "unknown"),
        service=service,
        frameworks=", ".join(active_frameworks) if active_frameworks else "None",
        maturity=profile.get("complianceMaturity", "not-started"),
        cost_pressure=profile.get("costPressure", 3),
        risk_tolerance=profile.get("riskTolerance", 3),
        security=weights.get("security", 0.50),
        compliance_text=compliance_text if compliance_text else "No compliance reference available.",
        inline_reason=inline_reason,
    )

    # Build messages for Bedrock (only content and role, filter to this field's conversation)
    bedrock_messages = []
    for msg in history:
        if msg.get("fieldId") == field_id or not msg.get("fieldId"):
            bedrock_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

    ai_response = call_bedrock_conversation(system_prompt, bedrock_messages)

    # ── Step 6: Parse UPDATE_FIELD signal ──────────────────────
    config_update = None
    display_text = ai_response

    if "UPDATE_FIELD:" in ai_response:
        parts = ai_response.split("UPDATE_FIELD:")
        display_text = parts[0].strip()
        try:
            update_json = parts[1].strip()
            # Find JSON in the update signal
            start = update_json.find("{")
            end = update_json.rfind("}") + 1
            if start != -1 and end > start:
                config_update = json.loads(update_json[start:end])
        except (json.JSONDecodeError, IndexError):
            pass  # If parsing fails, ignore the update signal

    # ── Step 7: Save to DynamoDB ───────────────────────────────
    history.append({
        "role": "assistant",
        "content": display_text,
        "fieldId": field_id,
    })
    update_session(session_id, "conversationHistory", history)

    if config_update:
        # Update the config value and reason together
        fid = config_update.get("fieldId", field_id)
        config[fid] = {
            "value": config_update["newValue"],
            "reason": config_update["newReason"],
        }
        update_session(session_id, "generatedConfig", config)

    # ── Step 8: Return response ────────────────────────────────
    return {
        "response": display_text,
        "configUpdate": config_update,
    }
