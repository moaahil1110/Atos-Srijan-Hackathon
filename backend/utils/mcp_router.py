from mcp import StdioServerParameters

from config import settings

PROVIDER_MCP_CONFIG = {
    "aws": StdioServerParameters(
        command=settings.AWS_MCP_COMMAND,
        args=settings.AWS_MCP_ARGS.split(),
        env={"FASTMCP_LOG_LEVEL": "ERROR"},
    ),
    "azure": StdioServerParameters(
        command=settings.AZURE_MCP_COMMAND,
        args=settings.AZURE_MCP_ARGS.split(),
        env={"FASTMCP_LOG_LEVEL": "ERROR"},
    ),
    "gcp": StdioServerParameters(
        command=settings.GCP_MCP_COMMAND,
        args=settings.GCP_MCP_ARGS.split(),
        env={"FASTMCP_LOG_LEVEL": "ERROR"},
    ),
}


def get_mcp_params(provider: str) -> StdioServerParameters:
    provider = provider.lower()
    if provider not in PROVIDER_MCP_CONFIG:
        raise ValueError(f"Provider '{provider}' not supported.")
    return PROVIDER_MCP_CONFIG[provider]


def get_mcp_url(provider: str) -> str:
    provider = provider.lower()
    if provider == "aws":
        return settings.AWS_MCP_URL
    if provider == "azure":
        return settings.AZURE_MCP_URL
    if provider == "gcp":
        return settings.GCP_MCP_URL
    raise ValueError(f"Provider '{provider}' not supported.")


def get_mcp_auth_token(provider: str) -> str:
    provider = provider.lower()
    if provider == "aws":
        return settings.AWS_MCP_AUTH_TOKEN
    if provider == "azure":
        return settings.AZURE_MCP_AUTH_TOKEN
    if provider == "gcp":
        return settings.GCP_MCP_AUTH_TOKEN
    raise ValueError(f"Provider '{provider}' not supported.")


def is_provider_supported(provider: str) -> bool:
    return provider.lower() in PROVIDER_MCP_CONFIG
