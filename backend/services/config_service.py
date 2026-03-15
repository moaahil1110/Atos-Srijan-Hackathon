# Config generation service
# 1. Load session from DynamoDB
# 2. Fetch relevant compliance docs from S3
# 3. Build prompt with weights + fields + compliance text
# 4. Call Bedrock — every field gets value + reason
# 5. Save config to DynamoDB
# 6. Return config map

import json
import logging

from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import get_session, update_session
from utils.compliance_mapper import fetch_compliance_text
from services.field_classifier import classify_field

logger = logging.getLogger(__name__)

_CONFIG_PROMPT = """\
You are configuring AWS {service} for a specific company.

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

Return ONLY a JSON object where each key is a fieldId and each value
is an object with exactly two keys:
  value: the recommended setting (boolean, string, or number)
  reason: one sentence — must be specific to this company, must cite
          compliance clause number if reference text contains one

Critical rules:
- LOCKED_SECURE fields: most secure value, zero exceptions
- PREFER_SECURE fields: secure value strongly preferred
- OPTIMISE_COST fields: cost-efficient option permitted
- BALANCED fields: use judgement based on profile
- Security is NEVER relaxed for cost reasons
- BAD reason: "Encryption is important for security"
- GOOD reason: "HIPAA §164.312(e)(2)(ii) requires encryption of ePHI for your patient data workload"
"""


async def generate_config(
    session_id: str,
    schema_data: dict | list,
    service: str,
) -> dict:
    """
    Generate configuration for an AWS service by:
      1. Loading the session (profile + weights) from DynamoDB
      2. Classifying each field with instruction tags
      3. Fetching relevant compliance docs
      4. Calling Bedrock with a mega-prompt
      5. Saving + returning the config map
    """
    # 1. Load session
    session = get_session(session_id)
    profile = session["companyProfile"]
    weights = session["computedWeights"]

    # Ensure weights are floats (DynamoDB stores Decimal)
    weights = {k: float(v) for k, v in weights.items()}

    active_frameworks = profile.get("complianceFrameworks", [])
    maturity = profile.get("complianceMaturity", "not-started")

    # 2. Get the fields list
    if isinstance(schema_data, dict):
        fields = schema_data.get("fields", [])
    elif isinstance(schema_data, list):
        fields = schema_data
    else:
        fields = []

    # 3. Classify each field
    classified_fields = [
        classify_field(f, weights, active_frameworks, maturity)
        for f in fields
    ]

    # 4. Fetch compliance text (RAG)
    compliance_text = fetch_compliance_text(active_frameworks, classified_fields)
    if not compliance_text:
        compliance_text = "(No matching compliance documents found)"

    # 5. Build prompt
    prompt = _CONFIG_PROMPT.format(
        service=service,
        security=weights.get("security", 0),
        compliance=weights.get("compliance", 0),
        cost=weights.get("cost", 0),
        industry=profile.get("industry", "unknown"),
        frameworks=", ".join(active_frameworks) if active_frameworks else "none",
        maturity=maturity,
        cost_pressure=profile.get("costPressure", 3),
        risk_tolerance=profile.get("riskTolerance", 3),
        weight_reasoning=profile.get("weightReasoning", "N/A"),
        compliance_text=compliance_text,
        fields_json=json.dumps(classified_fields, indent=2),
    )

    # 6. Call Bedrock
    config_map = invoke_bedrock_json(prompt)

    # 7. Save to DynamoDB
    update_session(session_id, "generatedConfig", config_map)
    update_session(session_id, "selectedService", service)

    logger.info("Generated config for session %s — %d fields", session_id, len(config_map))

    return config_map
