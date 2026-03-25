import os

from config import settings
from utils.s3_client import get_object

COMPLIANCE_FILES = {
    "HIPAA": ["hipaa-encryption.txt", "hipaa-access-controls.txt", "hipaa-logging.txt"],
    "PCI-DSS": ["pcidss-encryption.txt", "pcidss-access.txt", "pcidss-logging.txt"],
    "SOC2": ["soc2-access.txt", "soc2-logging.txt"],
    "ISO27001": [],
    "GDPR": [],
}


def _read_local(filename: str) -> str:
    path = os.path.join(settings.COMPLIANCE_DOCS_DIR, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def get_text(frameworks: list[str], field_keywords: list[str]) -> str:
    docs = []
    for framework in frameworks or ["none"]:
        for filename in COMPLIANCE_FILES.get(framework, []):
            content = ""
            try:
                content = get_object(settings.S3_BUCKET, f"compliance/{filename}") or ""
            except Exception:
                content = ""
            if not content:
                content = _read_local(filename)
            if content:
                docs.append(content)
    return "\n\n---\n\n".join(docs)
