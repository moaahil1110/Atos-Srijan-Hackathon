# Intent extraction service
# 1. Call Bedrock to extract structured profile from description
# 2. Call weights_engine.compute_weights()
# 3. Save session to DynamoDB
# 4. Return sessionId + intent + weights

import uuid
import logging
from datetime import datetime, timezone

from services.weights_engine import compute_weights
from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import save_session

logger = logging.getLogger(__name__)

_INTENT_PROMPT = """\
Extract structured business context from this company description.
Return ONLY valid JSON with these exact fields:
  industry, complianceFrameworks (array), complianceMaturity,
  teamSize, costPressure (1-5 integer), riskTolerance (1-5 integer),
  missionCriticalServices (array), dataClassification, weightReasoning

Hard rules:
- costPressure and riskTolerance must be integers 1 to 5
- complianceFrameworks must be an array even if empty
- If no compliance mentioned, use empty array []
- complianceMaturity must be one of: "certified", "in-progress", "not-started"
- dataClassification must be one of: "highly-confidential", "confidential", "internal", "public"
- Return ONLY the JSON object, no preamble

Company description:
{description}
"""


async def extract_intent(description: str) -> dict:
    """
    Takes a company description string, calls Bedrock to extract a structured
    company profile, computes priority weights, saves the session, and returns
    the session payload.
    """
    # 1. Call Bedrock to get company profile
    prompt = _INTENT_PROMPT.format(description=description)
    company_profile = invoke_bedrock_json(prompt)

    # Ensure required fields have valid types
    company_profile.setdefault("complianceFrameworks", [])
    company_profile.setdefault("costPressure", 3)
    company_profile.setdefault("riskTolerance", 3)
    company_profile.setdefault("dataClassification", "internal")
    company_profile.setdefault("complianceMaturity", "not-started")

    # Clamp integer fields
    company_profile["costPressure"] = max(1, min(5, int(company_profile["costPressure"])))
    company_profile["riskTolerance"] = max(1, min(5, int(company_profile["riskTolerance"])))

    # 2. Compute weights
    weights = compute_weights(company_profile)

    # 3. Generate session ID
    session_id = str(uuid.uuid4())

    # 4. Save to DynamoDB
    session_item = {
        "sessionId": session_id,
        "companyProfile": company_profile,
        "computedWeights": weights,
        "conversationHistory": [],
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    save_session(session_item)

    logger.info("Created session %s with weights %s", session_id, weights)

    # 5. Return
    return {
        "sessionId": session_id,
        "intent": company_profile,
        "weights": weights,
    }
