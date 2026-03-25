import json
import logging
import re
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from config import settings

logger = logging.getLogger(__name__)
_client = None


def _get_client():
    global _client
    if _client is None:
        kwargs = {"region_name": settings.AWS_REGION}
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
        if settings.AWS_SESSION_TOKEN:
            kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN
        kwargs["config"] = Config(connect_timeout=1, read_timeout=2, retries={"max_attempts": 1})
        _client = boto3.client("bedrock-runtime", **kwargs)
    return _client


def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "")
        return code in {
            "ThrottlingException",
            "TooManyRequestsException",
            "InternalServerException",
            "ServiceUnavailableException",
            "ModelTimeoutException",
        }
    return False


def invoke_bedrock(
    prompt: str,
    system: str | None = None,
    messages: list[dict] | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> str:
    if messages is None:
        messages = [{"role": "user", "content": [{"text": prompt}]}]

    payload = {
        "modelId": settings.BEDROCK_MODEL_ID,
        "messages": messages,
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    }
    if system:
        payload["system"] = [{"text": system}]

    backoffs = [1, 2, 4]
    last_error = None
    for attempt, delay in enumerate(backoffs, start=1):
        try:
            response = _get_client().converse(**payload)
            return response["output"]["message"]["content"][0]["text"]
        except Exception as exc:  # pragma: no cover - depends on AWS
            last_error = exc
            if not _is_retryable(exc) or attempt == len(backoffs):
                break
            logger.warning("Bedrock call failed on attempt %s, retrying: %s", attempt, exc)
            time.sleep(delay)
    raise last_error


def _parse_json(raw_text: str):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        array_match = re.search(r"\[.*\]", raw_text, re.DOTALL)
        if array_match:
            return json.loads(array_match.group())
        raise


def invoke_bedrock_json(
    prompt: str,
    system: str | None = None,
    messages: list[dict] | None = None,
    max_retries: int = 3,
):
    retry_prompt = prompt
    retry_messages = messages
    for attempt in range(max_retries):
        raw_text = invoke_bedrock(retry_prompt, system=system, messages=retry_messages)
        try:
            return _parse_json(raw_text)
        except json.JSONDecodeError:
            if attempt == max_retries - 1:
                raise
            suffix = "\n\nIMPORTANT: Return ONLY valid JSON. No prose, no markdown fences."
            retry_prompt = f"{retry_prompt}{suffix}"
            if retry_messages:
                retry_messages = [dict(message) for message in retry_messages]
                last_message = retry_messages[-1]
                if last_message["role"] == "user" and last_message.get("content"):
                    retry_messages[-1] = {
                        **last_message,
                        "content": [{"text": last_message["content"][0]["text"] + suffix}],
                    }
    raise ValueError("Failed to parse Bedrock response as JSON after retries.")
