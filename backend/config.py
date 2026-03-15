# config.py — loads .env vars into a settings object

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central settings loaded from environment variables."""

    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DYNAMO_TABLE: str = os.getenv("DYNAMO_TABLE", "nimbus-sessions")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "nimbus-compliance-docs")
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID",
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    SCHEMAS_DIR: str = os.getenv(
        "SCHEMAS_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas"),
    )
    COMPLIANCE_DOCS_DIR: str = os.getenv(
        "COMPLIANCE_DOCS_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "compliance-docs"),
    )


settings = Settings()
