"""Intent extraction service — Person 1 owns this.
1. Call Bedrock to extract structured profile from description
2. Call weights_engine.compute_weights()
3. Save session to DynamoDB
4. Return sessionId + intent + weights
"""
import uuid
import time
from utils.bedrock_client import call_bedrock_json
from utils.dynamo_client import save_session
from services.weights_engine import compute_weights

EXTRACTION_PROMPT = """Extract structured business context from this company description.
Return ONLY valid JSON with these exact fields:
{
  "industry": "string",
  "complianceFrameworks": ["array of framework names like HIPAA, PCI-DSS, SOC2"],
  "complianceMaturity": "achieved or in-progress or not-started",
  "teamSize": "string like small, medium, large",
  "costPressure": 3,
  "riskTolerance": 3,
  "missionCriticalServices": ["array of AWS service names"],
  "dataClassification": "highly-confidential or confidential or internal or public",
  "weightReasoning": "one sentence explaining the company profile"
}

Hard rules:
- costPressure and riskTolerance must be integers 1 to 5
- complianceFrameworks must be an array even if empty
- If no compliance mentioned, use empty array []
- complianceMaturity must be one of: achieved, in-progress, not-started
- dataClassification must be one of: highly-confidential, confidential, internal, public
- Return ONLY the JSON object, no preamble, no markdown"""


def extract_intent(description: str) -> dict:
    """Extract company intent from description, compute weights, save session."""

    # ── Step 1: Bedrock extracts structured profile ────────────
    profile = call_bedrock_json(
        EXTRACTION_PROMPT,
        f"Company description:\n{description}"
    )

    # ── Step 2: Compute deterministic weights ──────────────────
    weights = compute_weights(profile)

    # ── Step 3: Generate session ID and save ───────────────────
    session_id = str(uuid.uuid4())
    session = {
        "sessionId": session_id,
        "companyProfile": profile,
        "computedWeights": weights,
        "conversationHistory": [],
        "createdAt": int(time.time()),
    }
    save_session(session)

    # ── Step 4: Return response ────────────────────────────────
    return {
        "sessionId": session_id,
        "intent": profile,
        "weights": weights,
    }
