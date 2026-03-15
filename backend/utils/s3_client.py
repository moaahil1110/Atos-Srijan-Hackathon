# Shared S3 helper
# get_object(bucket, key) -> str
# put_object(bucket, key, body) -> None

import json
import boto3
from botocore.exceptions import ClientError
from config import settings

# Lazy client — avoids crash at import if AWS creds missing
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client("s3", region_name=settings.AWS_REGION)
    return _client


def get_object(bucket: str, key: str) -> str | None:
    """Download an S3 object and return its body as a UTF-8 string. Returns None if 404."""
    try:
        resp = _get_client().get_object(Bucket=bucket, Key=key)
        return resp["Body"].read().decode("utf-8")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return None
        raise


def put_object(bucket: str, key: str, body: str) -> None:
    """Upload a UTF-8 string as an S3 object."""
    _get_client().put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))


def get_json(bucket: str, key: str) -> dict | None:
    """Read a JSON file from S3. Returns parsed dict or None if not found."""
    content = get_object(bucket, key)
    if content is not None:
        return json.loads(content)
    return None


def put_json(bucket: str, key: str, data: dict) -> None:
    """Write a JSON file to S3."""
    put_object(bucket, key, json.dumps(data, indent=2))
