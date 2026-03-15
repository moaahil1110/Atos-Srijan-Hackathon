# Shared DynamoDB helper
# get_session(session_id) -> dict
# save_session(item) -> None
# update_session(session_id, key, value) -> None

import json
from decimal import Decimal

import boto3
from config import settings

# Lazy table reference — avoids crash at import if AWS creds missing
_table = None


def _get_table():
    global _table
    if _table is None:
        _table = boto3.resource(
            "dynamodb", region_name=settings.AWS_REGION
        ).Table(settings.DYNAMO_TABLE)
    return _table


def _convert_decimals(obj):
    """Recursively convert DynamoDB Decimal types back to int/float."""
    if isinstance(obj, Decimal):
        return int(obj) if obj == int(obj) else float(obj)
    if isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals(i) for i in obj]
    return obj


def _convert_floats(obj):
    """Recursively convert floats to Decimal for DynamoDB storage."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _convert_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_floats(i) for i in obj]
    return obj


def get_session(session_id: str) -> dict:
    """Fetch a session by its sessionId. Raises KeyError if not found."""
    resp = _get_table().get_item(Key={"sessionId": session_id})
    item = resp.get("Item")
    if not item:
        raise KeyError(f"Session {session_id} not found")
    return _convert_decimals(item)


def save_session(item: dict) -> None:
    """Put a full session item into DynamoDB."""
    _get_table().put_item(Item=_convert_floats(item))


def update_session(session_id: str, key: str, value) -> None:
    """Update a single top-level attribute on an existing session."""
    _get_table().update_item(
        Key={"sessionId": session_id},
        UpdateExpression="SET #k = :v",
        ExpressionAttributeNames={"#k": key},
        ExpressionAttributeValues={":v": _convert_floats(value)},
    )
