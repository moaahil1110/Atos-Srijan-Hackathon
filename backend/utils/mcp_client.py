import json
import logging

import httpx
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

from utils.mcp_router import get_mcp_auth_token, get_mcp_params, get_mcp_url

logger = logging.getLogger(__name__)

_TOOL_PRIORITY = (
    "search",
    "query",
    "docs",
    "document",
    "fetch",
    "lookup",
    "read",
    "ask",
)

_ARGUMENT_CANDIDATES = (
    "query",
    "q",
    "text",
    "prompt",
    "topic",
    "service_name",
    "service",
    "name",
    "input",
)


def _choose_tool(tools: list) -> object | None:
    if not tools:
        return None
    ordered = sorted(
        tools,
        key=lambda tool: min(
            (
                index
                for index, candidate in enumerate(_TOOL_PRIORITY)
                if candidate in tool.name.lower()
            ),
            default=len(_TOOL_PRIORITY),
        ),
    )
    return ordered[0]


def _build_arguments(tool, query: str) -> dict:
    schema = getattr(tool, "inputSchema", {}) or {}
    properties = schema.get("properties", {})
    if not properties:
        return {"query": query}

    for candidate in _ARGUMENT_CANDIDATES:
        if candidate in properties:
            return {candidate: query}

    first_property = next(iter(properties))
    return {first_property: query}


def _extract_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        parts = [_extract_text(item) for item in value]
        return "\n".join(part for part in parts if part)
    if isinstance(value, dict):
        direct = []
        for key in ("text", "content", "result", "output", "data", "structuredContent"):
            if key in value:
                direct.append(_extract_text(value[key]))
        if direct:
            return "\n".join(part for part in direct if part)
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


async def fetch_service_docs(service_name: str, provider: str = "aws") -> str:
    mcp_url = get_mcp_url(provider)
    try:
        if mcp_url:
            headers = {}
            auth_token = get_mcp_auth_token(provider)
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            if headers:
                async with httpx.AsyncClient(headers=headers) as http_client:
                    async with streamable_http_client(mcp_url, http_client=http_client) as (read, write, _):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            tools_response = await session.list_tools()
                            tool = _choose_tool(getattr(tools_response, "tools", []))
                            if tool is None:
                                return ""
                            arguments = _build_arguments(tool, service_name)
                            result = await session.call_tool(tool.name, arguments=arguments)
                            text = _extract_text(getattr(result, "content", None))
                            if text:
                                return text
                            return _extract_text(getattr(result, "structuredContent", None))
            transport = streamable_http_client(mcp_url)
        else:
            transport = stdio_client(get_mcp_params(provider))
        async with transport as transport_streams:
            if len(transport_streams) == 3:
                read, write, _ = transport_streams
            else:
                read, write = transport_streams
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                tool = _choose_tool(getattr(tools_response, "tools", []))
                if tool is None:
                    return ""
                arguments = _build_arguments(tool, service_name)
                result = await session.call_tool(tool.name, arguments=arguments)
                text = _extract_text(getattr(result, "content", None))
                if text:
                    return text
                return _extract_text(getattr(result, "structuredContent", None))
    except Exception as exc:
        logger.warning("MCP connection failed for %s/%s: %s", provider, service_name, exc)
        raise
