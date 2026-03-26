import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)
load_dotenv(override=True)


class Settings:
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "5000"))

    AWS_REGION: str = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    DYNAMO_TABLE: str = os.getenv("DYNAMO_TABLE", os.getenv("DYNAMODB_TABLE", "nimbus-sessions"))
    S3_BUCKET: str = os.getenv("S3_BUCKET", os.getenv("COMPLIANCE_BUCKET", "nimbus-compliance-docs"))
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID",
        os.getenv("MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"),
    )
    BEDROCK_KB_ID: str = os.getenv("BEDROCK_KB_ID", "")

    AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: str | None = os.getenv("AWS_SESSION_TOKEN")

    BEDROCK_AWS_ACCESS_KEY_ID: str | None = os.getenv("BEDROCK_AWS_ACCESS_KEY_ID")
    BEDROCK_AWS_SECRET_ACCESS_KEY: str | None = os.getenv("BEDROCK_AWS_SECRET_ACCESS_KEY")

    AZURE_MCP_COMMAND: str = os.getenv("AZURE_MCP_COMMAND", "uvx")
    AZURE_MCP_ARGS: str = os.getenv("AZURE_MCP_ARGS", "azure-mcp@latest")
    AZURE_MCP_URL: str = os.getenv("AZURE_MCP_URL", "")
    AZURE_MCP_AUTH_TOKEN: str = os.getenv("AZURE_MCP_AUTH_TOKEN", "")
    GCP_MCP_COMMAND: str = os.getenv("GCP_MCP_COMMAND", "uvx")
    GCP_MCP_ARGS: str = os.getenv("GCP_MCP_ARGS", "gcp-mcp@latest")
    GCP_MCP_URL: str = os.getenv("GCP_MCP_URL", "")
    GCP_MCP_AUTH_TOKEN: str = os.getenv("GCP_MCP_AUTH_TOKEN", "")
    AWS_MCP_COMMAND: str = os.getenv(
        "AWS_MCP_COMMAND",
        "uvx",
    )
    AWS_MCP_ARGS: str = os.getenv(
        "AWS_MCP_ARGS",
        "awslabs.aws-documentation-mcp-server@latest",
    )
    AWS_MCP_URL: str = os.getenv("AWS_MCP_URL", "")
    AWS_MCP_AUTH_TOKEN: str = os.getenv("AWS_MCP_AUTH_TOKEN", "")
    SUPPORTED_PROVIDERS: tuple[str, ...] = ("aws", "azure", "gcp")

    BASE_DIR: str = os.path.dirname(__file__)
    SCHEMAS_DIR: str = os.path.join(BASE_DIR, "schemas")
    COMPLIANCE_DOCS_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "compliance-docs")


settings = Settings()
