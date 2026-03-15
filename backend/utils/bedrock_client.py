"""Shared boto3 Bedrock client — uses Converse API with JSON retry.
Uses SEPARATE AWS credentials for Bedrock (Hamdan's account)."""
import json
import os
import boto3
from config import AWS_REGION, MODEL_ID

# Build a separate session for Bedrock using dedicated credentials
_bedrock_key = os.getenv("BEDROCK_AWS_ACCESS_KEY_ID", "")
_bedrock_secret = os.getenv("BEDROCK_AWS_SECRET_ACCESS_KEY", "")

if _bedrock_key and _bedrock_secret:
    _bedrock_session = boto3.Session(
        aws_access_key_id=_bedrock_key,
        aws_secret_access_key=_bedrock_secret,
        region_name=AWS_REGION,
    )
    bedrock = _bedrock_session.client("bedrock-runtime", region_name=AWS_REGION)
else:
    # Fallback to default credentials
    bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def call_bedrock(system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
    """Call Bedrock using the Converse API. Returns the text response."""
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[
            {"role": "user", "content": [{"text": user_message}]}
        ],
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.2},
    )
    return response["output"]["message"]["content"][0]["text"]


def call_bedrock_json(system_prompt: str, user_message: str, max_tokens: int = 4096) -> dict:
    """Call Bedrock and parse response as JSON. Retries once on parse failure."""
    raw = call_bedrock(system_prompt, user_message, max_tokens)

    # Try to extract JSON from the response
    try:
        return _extract_json(raw)
    except (json.JSONDecodeError, ValueError):
        pass

    # Retry with stricter prompt
    retry_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY a valid JSON object. No markdown, no preamble, no explanation. "
        "Just the raw JSON object starting with { and ending with }."
    )
    raw = call_bedrock(system_prompt + "\n\n" + retry_prompt, user_message, max_tokens)
    return _extract_json(raw)


def call_bedrock_conversation(system_prompt: str, messages: list, max_tokens: int = 4096) -> str:
    """Call Bedrock with full conversation history. Returns text response."""
    # Convert our message format to Bedrock's format
    bedrock_messages = []
    for msg in messages:
        bedrock_messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=bedrock_messages,
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.3},
    )
    return response["output"]["message"]["content"][0]["text"]


def _extract_json(text: str) -> dict:
    """Extract JSON from text that might contain markdown fences or preamble."""
    text = text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    # Find the first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start:end + 1])

    raise ValueError(f"No JSON object found in response: {text[:200]}")
