"""Terraform export service (stretch goal — attempt hour 8).
1. Load session config from DynamoDB
2. Extract values only (drop reasons)
3. Call Bedrock to generate .tf file
4. Return terraform content string
"""
import json
from utils.bedrock_client import call_bedrock
from utils.dynamo_client import get_session

TERRAFORM_PROMPT = """You are a Terraform expert. Generate a valid Terraform (.tf) file
for the given AWS service configuration. Use the exact field values provided.

Rules:
- Use proper Terraform HCL syntax
- Use the aws provider
- Include all provided configuration values
- Add appropriate variable references where sensible
- Include comments explaining each setting
- Return ONLY the .tf file content, no markdown fences, no explanation"""


def export_terraform(session_id: str) -> dict:
    """Generate a Terraform file from the session's generated config."""

    # ── Step 1: Load session ───────────────────────────────────
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    config = session.get("generatedConfig", {})
    service = session.get("selectedService", "S3")

    if not config:
        raise ValueError("No generated config found for this session")

    # ── Step 2: Extract values only ────────────────────────────
    values_only = {}
    for field_id, field_data in config.items():
        if isinstance(field_data, dict):
            values_only[field_id] = field_data.get("value", field_data)
        else:
            values_only[field_id] = field_data

    # ── Step 3: Call Bedrock ───────────────────────────────────
    tf_content = call_bedrock(
        TERRAFORM_PROMPT,
        f"Generate a Terraform file for AWS {service} with these settings:\n"
        f"{json.dumps(values_only, indent=2)}"
    )

    # Clean up any markdown fencing
    if tf_content.startswith("```"):
        lines = tf_content.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        tf_content = "\n".join(lines)

    return {"terraformContent": tf_content}
