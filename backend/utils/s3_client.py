"""Shared S3 helper for schema cache and compliance docs."""
import json
import boto3
from botocore.exceptions import ClientError
from config import AWS_REGION

s3 = boto3.client("s3", region_name=AWS_REGION)


def get_object(bucket: str, key: str) -> str | None:
    """Read a file from S3. Returns content string or None if not found."""
    try:
        resp = s3.get_object(Bucket=bucket, Key=key)
        return resp["Body"].read().decode("utf-8")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return None
        raise


def get_json(bucket: str, key: str) -> dict | None:
    """Read a JSON file from S3. Returns parsed dict or None if not found."""
    content = get_object(bucket, key)
    if content is not None:
        return json.loads(content)
    return None


def put_object(bucket: str, key: str, body: str) -> None:
    """Write a file to S3."""
    s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))


def put_json(bucket: str, key: str, data: dict) -> None:
    """Write a JSON file to S3."""
    put_object(bucket, key, json.dumps(data, indent=2))
