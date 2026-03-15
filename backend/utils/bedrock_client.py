# Shared boto3 Bedrock client
# Call bedrock using converse() API
# Handles JSON parsing + retry on malformed response

import json
import re
import logging

import boto3

from config import settings

logger = logging.getLogger(__name__)

# Lazy client — created on first call, not at import time.
# This avoids crashing if AWS creds aren't configured yet (e.g. during tests).
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
        )
    return _client


def invoke_bedrock(
    prompt: str,
    system: str | None = None,
    messages: list[dict] | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.3,
) -> str:
    """
    Call Bedrock via the Converse API.
    Accepts either:
      - a simple `prompt` string  (turned into a single user message), OR
      - a full `messages` list     (for multi-turn conversations)
    Returns the raw text content from the model.
    """
    if messages is None:
        messages = [
            {"role": "user", "content": [{"text": prompt}]},
        ]

    kwargs = {
        "modelId": settings.BEDROCK_MODEL_ID,
        "messages": messages,
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    }
    if system:
        kwargs["system"] = [{"text": system}]

    response = _get_client().converse(**kwargs)
    return response["output"]["message"]["content"][0]["text"]


def invoke_bedrock_json(
    prompt: str,
    system: str | None = None,
    max_retries: int = 2,
) -> dict:
    """
    Call Bedrock and parse the response as JSON.
    Strategy:
      1. Try json.loads(response) directly
      2. If fails: regex-extract first { ... } block
      3. If still fails: retry with a stricter prompt
    """
    for attempt in range(max_retries + 1):
        raw = invoke_bedrock(prompt, system=system)

        # Attempt 1: direct parse
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Attempt 2: regex extract first JSON object
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Retry with stricter instruction
        if attempt < max_retries:
            logger.warning(
                "Bedrock JSON parse failed (attempt %d), retrying with stricter prompt",
                attempt + 1,
            )
            prompt = (
                f"{prompt}\n\n"
                "IMPORTANT: Your previous response was not valid JSON. "
                "Return ONLY a valid JSON object, no markdown, no preamble."
            )

    raise ValueError(f"Failed to parse Bedrock response as JSON after {max_retries + 1} attempts")
