"""Config generation service — Person 1 owns this.
1. Load session from DynamoDB
2. Fetch relevant compliance docs from S3
3. Build prompt with weights + fields + compliance text
4. Call Bedrock — every field gets value + reason
5. Save config to DynamoDB
6. Return config map
"""
import json
from utils.bedrock_client import call_bedrock_json
from utils.dynamo_client import get_session, update_session
from utils.compliance_mapper import fetch_primary_compliance_text

CONFIG_SYSTEM_PROMPT = """You are configuring AWS {service} for a specific company.

ENFORCED priority weights — computed by backend, do not override:
Security: {security}
Compliance: {compliance}
Cost: {cost}

Company profile:
Industry: {industry}
Compliance: {frameworks} ({maturity})
Cost pressure: {cost_pressure}/5
Risk tolerance: {risk_tolerance}/5
Weight reasoning: {weight_reasoning}

Compliance reference text:
{compliance_text}

Fields to configure:
{fields_json}

Return ONLY a JSON object where each key is a fieldId and each value is an object with exactly two keys:
  "value": the recommended setting (boolean, string, or number)
  "reason": one sentence — must be specific to this company, must cite compliance clause number if reference text contains a relevant one, never generic

Critical rules:
- LOCKED_SECURE fields: most secure value, zero exceptions
- PREFER_SECURE fields: secure value strongly preferred
- OPTIMISE_COST fields: cost-efficient option permitted
- BALANCED fields: use judgement based on profile
- Security is NEVER relaxed for cost reasons
- BAD reason: "Encryption is important for security"
- GOOD reason: "HIPAA §164.312(e)(2)(ii) requires encryption of ePHI for your patient data workload"
- Return ONLY the JSON, no explanation"""


def generate_config(session_id: str, schema: dict, service: str) -> dict:
    """Generate tailored config values for every field in the schema."""

    # ── Step 1: Load session ───────────────────────────────────
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    profile = session.get("companyProfile", {})
    weights = session.get("computedWeights", {})

    # ── Step 2: Fetch compliance text ──────────────────────────
    active_frameworks = profile.get("complianceFrameworks", [])
    compliance_text = fetch_primary_compliance_text(active_frameworks, service)

    # ── Step 3: Build prompt ───────────────────────────────────
    fields = schema.get("fields", [])
    fields_for_prompt = []
    for f in fields:
        fields_for_prompt.append({
            "fieldId": f.get("fieldId"),
            "label": f.get("label"),
            "type": f.get("type"),
            "options": f.get("options"),
            "instruction": f.get("instruction", "BALANCED"),
            "securityRelevance": f.get("securityRelevance"),
            "complianceRelevance": f.get("complianceRelevance", []),
        })

    system_prompt = CONFIG_SYSTEM_PROMPT.format(
        service=service,
        security=weights.get("security", 0.50),
        compliance=weights.get("compliance", 0.25),
        cost=weights.get("cost", 0.25),
        industry=profile.get("industry", "unknown"),
        frameworks=", ".join(active_frameworks) if active_frameworks else "None",
        maturity=profile.get("complianceMaturity", "not-started"),
        cost_pressure=profile.get("costPressure", 3),
        risk_tolerance=profile.get("riskTolerance", 3),
        weight_reasoning=profile.get("weightReasoning", ""),
        compliance_text=compliance_text if compliance_text else "No compliance reference available.",
        fields_json=json.dumps(fields_for_prompt, indent=2),
    )

    # ── Step 4: Call Bedrock ───────────────────────────────────
    config = call_bedrock_json(
        system_prompt,
        f"Generate the configuration for AWS {service} based on the company profile and field instructions above."
    )

    # ── Step 5: Save to DynamoDB ───────────────────────────────
    update_session(session_id, "generatedConfig", config)
    update_session(session_id, "selectedService", service)

    return config
