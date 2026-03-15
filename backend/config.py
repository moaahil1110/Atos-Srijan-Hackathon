# config.py — loads .env vars into a settings object

import os
from dotenv import load_dotenv

# Override to ensure local .env takes precedence
load_dotenv(override=True)

# Clear any dummy credential values that might have been set previously
for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]:
    val = os.environ.get(key, "")
    if val.startswith("your_") or val == "":
        os.environ.pop(key, None)


class Settings:
    """Central settings loaded from environment variables."""

    # AWS Infrastructure (Person 2 names)
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))
    DYNAMO_TABLE: str = os.getenv("DYNAMODB_TABLE", "CopilotSessions")
    
    # Buckets
    S3_BUCKET: str = os.getenv("COMPLIANCE_BUCKET", "nimbus-compliance-docs")  # Fallback to previous
    SCHEMA_BUCKET: str = os.getenv("SCHEMA_BUCKET", "cloud-copilot-schemas")

    # Bedrock
    BEDROCK_MODEL_ID: str = os.getenv(
        "MODEL_ID",
        os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    )

    # Local paths
    SCHEMAS_DIR: str = os.getenv(
        "SCHEMAS_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas"),
    )
    COMPLIANCE_DOCS_DIR: str = os.getenv(
        "COMPLIANCE_DOCS_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "compliance-docs"),
    )


settings = Settings()
