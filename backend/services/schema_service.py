# Schema fetch service
# 1. Check local / S3 cache for schemas/aws/{service}.json
# 2. Run field_classifier on every field
# 3. Return classified schema

import json
import os
import logging

from config import settings
from utils.dynamo_client import get_session
from services.field_classifier import classify_field

logger = logging.getLogger(__name__)


async def get_schema(
    service: str,
    provider: str,
    session_id: str,
) -> dict:
    """
    Load the schema for a given service, classify each field using the
    session's weights, and return the enriched schema.
    """
    # 1. Load schema from local JSON
    schema_path = os.path.join(settings.SCHEMAS_DIR, provider, f"{service.lower()}.json")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema not found: {provider}/{service.lower()}.json")

    with open(schema_path, "r") as f:
        schema = json.load(f)

    # 2. Load session for weights
    session = get_session(session_id)
    weights = {k: float(v) for k, v in session["computedWeights"].items()}
    profile = session["companyProfile"]
    active_frameworks = profile.get("complianceFrameworks", [])
    maturity = profile.get("complianceMaturity", "not-started")

    # 3. Classify each field
    raw_fields = schema.get("fields", [])
    classified_fields = [
        classify_field(f, weights, active_frameworks, maturity)
        for f in raw_fields
    ]

    schema["fields"] = classified_fields

    logger.info(
        "Loaded schema %s/%s — %d fields classified",
        provider, service, len(classified_fields),
    )

    return schema
