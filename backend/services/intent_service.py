import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from config import settings
from services.weights_engine import compute_weights
from utils.bedrock_client import invoke_bedrock, invoke_bedrock_json
from utils.dynamo_client import save_session
from utils.grounding import NIMBUS_SYSTEM_PROMPT
from utils.service_mapper import get_provider_label, normalize_provider

logger = logging.getLogger(__name__)

INTENT_PROMPT = """
Extract structured business context from this company description.

Description: "{description}"

Return ONLY valid JSON with these exact fields:
{
  "industry": "healthcare|fintech|ecommerce|saas|government|other",
  "complianceFrameworks": ["HIPAA|PCI-DSS|SOC2|ISO27001|GDPR|none"],
  "complianceMaturity": "certified|in-progress|not-started",
  "teamSize": "string description",
  "costPressure": 1-5,
  "riskTolerance": 1-5,
  "missionCriticalServices": ["list of services mentioned"],
  "dataClassification": "highly-confidential|confidential|internal|public",
  "weightReasoning": "one sentence explaining the profile"
}

Rules:
- costPressure and riskTolerance must be integers 1-5
- If multiple frameworks apply include all of them
- If no compliance mentioned use ["none"]
- Return ONLY the JSON object, no preamble
"""

SERVICE_DETECTION_PROMPT = """
A company has described themselves as:
"{description}"

Their profile:
- Industry: {industry}
- Compliance: {compliance_frameworks}
- Data classification: {data_classification}

Which {provider} services do they most urgently need
to configure securely? Consider what services they
likely use based on their description.

Rules:
- Maximum 6 services
- Order by security criticality for their context
- For healthcare always include: {healthcare_defaults}
- For fintech always include: {fintech_defaults}
- Always include the provider's primary identity service
- AWS options: S3, RDS, IAM, EC2, Lambda, CloudFront
- Azure options: Blob Storage, Azure Database for PostgreSQL, Azure Active Directory, Virtual Machines, Azure Functions, Azure CDN
- GCP options: Cloud Storage, Cloud SQL, Cloud IAM, Compute Engine, Cloud Functions, Cloud CDN

Return ONLY a valid JSON array:
["service1", "service2", "service3"]
"""

def _default_services(intent: dict, provider: str) -> list[str]:
    industry = intent.get("industry", "other")
    defaults = {
        "aws": {
            "healthcare": ["S3", "RDS", "IAM"],
            "fintech": ["IAM", "RDS", "Lambda"],
            "default": ["S3", "RDS", "IAM"],
        },
        "azure": {
            "healthcare": ["Blob Storage", "Azure Database for PostgreSQL", "Azure Active Directory"],
            "fintech": ["Azure Active Directory", "Azure Database for PostgreSQL", "Azure Functions"],
            "default": ["Blob Storage", "Azure Database for PostgreSQL", "Azure Active Directory"],
        },
        "gcp": {
            "healthcare": ["Cloud Storage", "Cloud SQL", "Cloud IAM"],
            "fintech": ["Cloud IAM", "Cloud SQL", "Cloud Functions"],
            "default": ["Cloud Storage", "Cloud SQL", "Cloud IAM"],
        },
    }
    provider_defaults = defaults.get(provider, defaults["aws"])
    return provider_defaults.get(industry, provider_defaults["default"])


async def detect_services(description: str, intent: dict, provider: str = "aws") -> list[str]:
    provider = normalize_provider(provider)
    prompt = SERVICE_DETECTION_PROMPT.format(
        description=description,
        industry=intent.get("industry", "other"),
        compliance_frameworks=", ".join(intent.get("complianceFrameworks", ["none"])),
        data_classification=intent.get("dataClassification", "internal"),
        provider=get_provider_label(provider),
        healthcare_defaults=", ".join(_default_services({"industry": "healthcare"}, provider)),
        fintech_defaults=", ".join(_default_services({"industry": "fintech"}, provider)),
    )

    stricter_prompt = prompt
    for attempt in range(3):
        try:
            raw_text = invoke_bedrock(stricter_prompt, system=NIMBUS_SYSTEM_PROMPT)
            try:
                parsed = json.loads(raw_text)
            except json.JSONDecodeError:
                start = raw_text.find("[")
                end = raw_text.rfind("]")
                if start == -1 or end == -1 or end <= start:
                    raise
                parsed = json.loads(raw_text[start : end + 1])
            if isinstance(parsed, list) and parsed:
                return parsed[:6]
        except Exception as exc:
            logger.warning("Service detection attempt %s failed: %s", attempt + 1, exc)
            stricter_prompt = f"{stricter_prompt}\n\nIMPORTANT: Return ONLY a JSON array."
            time.sleep(0.2 * (attempt + 1))
    raise RuntimeError(f"Service detection failed for {provider}.")


async def extract_intent(description: str, provider: str = "aws") -> dict:
    provider = normalize_provider(provider)
    if provider not in settings.SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported.")

    intent = invoke_bedrock_json(INTENT_PROMPT.replace("{description}", description), system=NIMBUS_SYSTEM_PROMPT)

    intent.setdefault("complianceFrameworks", ["none"])
    if not intent["complianceFrameworks"]:
        intent["complianceFrameworks"] = ["none"]
    intent["costPressure"] = max(1, min(5, int(intent.get("costPressure", 3))))
    intent["riskTolerance"] = max(1, min(5, int(intent.get("riskTolerance", 3))))

    weights = compute_weights(intent)
    suggested_services = await detect_services(description, intent, provider)
    session_id = str(uuid.uuid4())

    session_item = {
        "sessionId": session_id,
        "companyProfile": intent,
        "weights": weights,
        "computedWeights": weights,
        "selectedProvider": provider,
        "selectedService": "",
        "currentConfig": {},
        "generatedConfig": {},
        "decisionEvidence": {"compliance": [], "provider": []},
        "decisionEvidenceByService": {},
        "configuredServices": [],
        "suggestedServices": suggested_services,
        "provider": provider,
        "conversationHistory": [],
        "fieldConversationHistory": {},
        "terraformOutput": "",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    save_session(session_item)

    return {
        "sessionId": session_id,
        "intent": intent,
        "weights": weights,
        "suggestedServices": suggested_services,
    }
