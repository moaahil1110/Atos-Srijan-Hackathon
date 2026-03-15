"""Shared DynamoDB helper for CopilotSessions table."""
import json
import boto3
from decimal import Decimal
from config import AWS_REGION, DYNAMODB_TABLE

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)


class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal types from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def _convert_floats(obj):
    """Convert float values to Decimal for DynamoDB storage."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _convert_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_floats(i) for i in obj]
    return obj


def get_session(session_id: str) -> dict | None:
    """Fetch a session by sessionId. Returns None if not found."""
    resp = table.get_item(Key={"sessionId": session_id})
    item = resp.get("Item")
    if item:
        # Convert Decimals back to floats for the application
        return json.loads(json.dumps(item, cls=DecimalEncoder))
    return None


def save_session(item: dict) -> None:
    """Save a full session item to DynamoDB."""
    table.put_item(Item=_convert_floats(item))


def update_session(session_id: str, key: str, value) -> None:
    """Update a single top-level key on a session."""
    table.update_item(
        Key={"sessionId": session_id},
        UpdateExpression=f"SET #k = :v",
        ExpressionAttributeNames={"#k": key},
        ExpressionAttributeValues={":v": _convert_floats(value)},
    )
