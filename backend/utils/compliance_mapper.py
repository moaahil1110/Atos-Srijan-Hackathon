"""Maps (framework, field_type) → S3 compliance doc path.
Used by config_service and explain_service to fetch RAG context."""
from utils.s3_client import get_object
from config import COMPLIANCE_BUCKET

# Mapping: (framework_lower, category) → S3 key
_COMPLIANCE_MAP = {
    ("hipaa", "access"):     "compliance/hipaa-access-controls.txt",
    ("hipaa", "encryption"): "compliance/hipaa-encryption.txt",
    ("hipaa", "logging"):    "compliance/hipaa-logging.txt",
    ("pci-dss", "access"):     "compliance/pcidss-access.txt",
    ("pci-dss", "encryption"): "compliance/pcidss-encryption.txt",
    ("pci-dss", "logging"):    "compliance/pcidss-logging.txt",
    ("soc2", "access"):     "compliance/soc2-access.txt",
    ("soc2", "logging"):    "compliance/soc2-logging.txt",
}

# Keywords to detect field category from relevance tags
_ENCRYPTION_KEYWORDS = {"encryption", "encrypt", "kms", "sse", "tls", "ssl", "key"}
_LOGGING_KEYWORDS = {"logging", "log", "audit", "monitor", "cloudtrail", "cloudwatch", "trail"}
_ACCESS_KEYWORDS = {"access", "public", "acl", "policy", "iam", "mfa", "password", "auth", "permission"}


def _detect_category(field: dict) -> str:
    """Detect the compliance category of a field based on its fieldId and label."""
    field_id = field.get("fieldId", "").lower()
    label = field.get("label", "").lower()
    combined = f"{field_id} {label}"

    if any(kw in combined for kw in _ENCRYPTION_KEYWORDS):
        return "encryption"
    if any(kw in combined for kw in _LOGGING_KEYWORDS):
        return "logging"
    if any(kw in combined for kw in _ACCESS_KEYWORDS):
        return "access"
    return "access"  # Default to access controls


def fetch_compliance_text(field: dict, active_frameworks: list[str]) -> str:
    """Fetch the most relevant compliance text for a field + active frameworks.
    Returns concatenated compliance text or empty string if no match."""
    if not active_frameworks:
        return ""

    category = _detect_category(field)
    texts = []

    # Check field's complianceRelevance against active frameworks
    field_compliance = [f.lower() for f in field.get("complianceRelevance", [])]

    for framework in active_frameworks:
        fw_lower = framework.lower()
        if fw_lower not in field_compliance and field_compliance:
            continue  # This framework isn't relevant to this field

        key = _COMPLIANCE_MAP.get((fw_lower, category))
        if key:
            content = get_object(COMPLIANCE_BUCKET, key)
            if content:
                texts.append(content)

    return "\n\n---\n\n".join(texts) if texts else ""


def fetch_primary_compliance_text(active_frameworks: list[str], service: str) -> str:
    """Fetch the primary compliance text for a service configuration.
    Used by config_service for overall context grounding."""
    if not active_frameworks:
        return ""

    primary = active_frameworks[0].lower()
    texts = []

    # Fetch all categories for the primary framework
    for category in ["access", "encryption", "logging"]:
        key = _COMPLIANCE_MAP.get((primary, category))
        if key:
            content = get_object(COMPLIANCE_BUCKET, key)
            if content:
                texts.append(content)

    return "\n\n---\n\n".join(texts) if texts else ""
