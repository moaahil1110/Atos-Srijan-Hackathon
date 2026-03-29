import os
from pathlib import Path

from dotenv import load_dotenv

BASE_PATH = Path(__file__).resolve().parent
ROOT_PATH = BASE_PATH.parent

load_dotenv(ROOT_PATH / ".env", override=False)
load_dotenv(BASE_PATH / ".env", override=True)


def _resolve_path(value: str | None, fallback: Path) -> str:
    path = Path(value) if value else fallback
    if not path.is_absolute():
        path = ROOT_PATH / path
    return str(path)


class Settings:
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "5000"))
    BEDROCK_CONNECT_TIMEOUT: int = int(os.getenv("BEDROCK_CONNECT_TIMEOUT", "10"))
    BEDROCK_READ_TIMEOUT: int = int(os.getenv("BEDROCK_READ_TIMEOUT", "180"))

    AWS_REGION: str = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    DYNAMO_TABLE: str = os.getenv(
        "DYNAMODB_TABLE_NAME",
        os.getenv("DYNAMODB_TABLE", os.getenv("DYNAMO_TABLE", "nimbus-sessions")),
    )
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID",
        os.getenv("MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"),
    )

    AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: str | None = os.getenv("AWS_SESSION_TOKEN")
    BEDROCK_AWS_ACCESS_KEY_ID: str | None = os.getenv("BEDROCK_AWS_ACCESS_KEY_ID")
    BEDROCK_AWS_SECRET_ACCESS_KEY: str | None = os.getenv("BEDROCK_AWS_SECRET_ACCESS_KEY")
    BEDROCK_AWS_SESSION_TOKEN: str | None = os.getenv("BEDROCK_AWS_SESSION_TOKEN")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    COMPLIANCE_INDEX_PATH: str = _resolve_path(
        os.getenv("COMPLIANCE_INDEX_PATH"),
        ROOT_PATH / "embeddings" / "compliance_index",
    )
    AZURE_INDEX_PATH: str = _resolve_path(
        os.getenv("AZURE_INDEX_PATH"),
        ROOT_PATH / "embeddings" / "azure_index",
    )
    GCP_INDEX_PATH: str = _resolve_path(
        os.getenv("GCP_INDEX_PATH"),
        ROOT_PATH / "embeddings" / "gcp_index",
    )
    SUPPORTED_PROVIDERS: tuple[str, ...] = ("aws", "azure", "gcp")

    ROOT_DIR: str = str(ROOT_PATH)
    BASE_DIR: str = str(BASE_PATH)
    SCHEMAS_DIR: str = str(BASE_PATH / "schemas")
    COMPLIANCE_DOCS_DIR: str = _resolve_path(
        os.getenv("COMPLIANCE_DOCS_DIR"),
        ROOT_PATH / "docs" / "compliance",
    )
    AZURE_DOCS_DIR: str = _resolve_path(
        os.getenv("AZURE_DOCS_DIR"),
        ROOT_PATH / "docs" / "providers" / "azure",
    )
    GCP_DOCS_DIR: str = _resolve_path(
        os.getenv("GCP_DOCS_DIR"),
        ROOT_PATH / "docs" / "providers" / "gcp",
    )


settings = Settings()
