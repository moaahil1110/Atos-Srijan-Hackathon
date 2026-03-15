# Shared S3 helper
# get_object(bucket, key) -> str
# put_object(bucket, key, body) -> None

import boto3
from config import settings

# Lazy client — avoids crash at import if AWS creds missing
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client("s3", region_name=settings.AWS_REGION)
    return _client


def get_object(bucket: str, key: str) -> str:
    """Download an S3 object and return its body as a UTF-8 string."""
    resp = _get_client().get_object(Bucket=bucket, Key=key)
    return resp["Body"].read().decode("utf-8")


def put_object(bucket: str, key: str, body: str) -> None:
    """Upload a UTF-8 string as an S3 object."""
    _get_client().put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))
