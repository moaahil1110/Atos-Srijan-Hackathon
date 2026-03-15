# Maps (framework, field_type) -> S3 compliance doc path
# fetch_compliance_text(field, active_frameworks) -> str
# Used by config_service and explain_service

import os
import logging

from utils.s3_client import get_object
from config import settings

logger = logging.getLogger(__name__)

# Static mapping: (framework_lower, keyword) -> S3 key / local filename
_COMPLIANCE_MAP: dict[tuple[str, str], str] = {
    ("hipaa", "encryption"):  "hipaa-encryption.txt",
    ("hipaa", "access"):      "hipaa-access-controls.txt",
    ("hipaa", "logging"):     "hipaa-logging.txt",
    ("pci-dss", "encryption"): "pcidss-encryption.txt",
    ("pci-dss", "access"):     "pcidss-access.txt",
    ("pci-dss", "logging"):    "pcidss-logging.txt",
    ("soc2", "access"):        "soc2-access.txt",
    ("soc2", "logging"):       "soc2-logging.txt",
}

# Keywords to search for in field labels / IDs
_KEYWORDS = ["encryption", "access", "logging"]


def _match_keyword(field: dict) -> str | None:
    """Guess which compliance topic a field relates to by its ID / label."""
    text = (
        field.get("fieldId", "") + " " + field.get("label", "")
    ).lower()
    for kw in _KEYWORDS:
        if kw in text:
            return kw
    return None


def _load_local(filename: str) -> str | None:
    """Fallback: read from local compliance-docs directory."""
    path = os.path.join(settings.COMPLIANCE_DOCS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return None


def fetch_compliance_text(
    active_frameworks: list[str],
    fields: list[dict] | None = None,
    field: dict | None = None,
) -> str:
    """
    Collect all matching compliance doc text for the given frameworks + fields.

    Accepts either:
      - `fields` — a list of field dicts (used by config_service to gather all docs)
      - `field`  — a single field dict  (used by explain_service for one field)

    Returns concatenated compliance text, or empty string if nothing matches.
    """
    if field and not fields:
        fields = [field]
    if not fields:
        fields = []

    seen_keys: set[str] = set()
    docs: list[str] = []

    # Normalise framework names to lowercase for matching
    fw_lower = [fw.lower() for fw in active_frameworks]

    for f in fields:
        keyword = _match_keyword(f)
        if keyword is None:
            continue
        for fw in fw_lower:
            lookup = (fw, keyword)
            filename = _COMPLIANCE_MAP.get(lookup)
            if filename and filename not in seen_keys:
                seen_keys.add(filename)
                # Try S3 first, fall back to local file
                try:
                    text = get_object(settings.S3_BUCKET, f"compliance/{filename}")
                except Exception:
                    text = _load_local(filename)
                if text:
                    docs.append(f"--- {filename} ---\n{text}")

    # If no field-specific matches, try to grab all docs for each framework
    if not docs:
        for fw in fw_lower:
            for (map_fw, _kw), filename in _COMPLIANCE_MAP.items():
                if map_fw == fw and filename not in seen_keys:
                    seen_keys.add(filename)
                    try:
                        text = get_object(settings.S3_BUCKET, f"compliance/{filename}")
                    except Exception:
                        text = _load_local(filename)
                    if text:
                        docs.append(f"--- {filename} ---\n{text}")

    return "\n\n".join(docs)
