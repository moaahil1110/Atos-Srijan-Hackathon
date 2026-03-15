"""config.py — loads .env vars into a settings object"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Clear any dummy credential values that might have been set previously
for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]:
    val = os.environ.get(key, "")
    if val.startswith("your_") or val == "":
        os.environ.pop(key, None)

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "CopilotSessions")
SCHEMA_BUCKET = os.getenv("SCHEMA_BUCKET", "cloud-copilot-schemas")
COMPLIANCE_BUCKET = os.getenv("COMPLIANCE_BUCKET", "cloud-copilot-compliance")
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
