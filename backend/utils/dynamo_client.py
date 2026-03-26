import logging
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError

from config import settings

logger = logging.getLogger(__name__)
_table = None


def _get_table():
    global _table
    if _table is None:
        _table = boto3.resource(
            "dynamodb",
            region_name=settings.AWS_REGION,
            config=Config(connect_timeout=1, read_timeout=2, retries={"max_attempts": 1}),
        ).Table(settings.DYNAMO_TABLE)
    return _table


def _convert_decimals(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj == int(obj) else float(obj)
    if isinstance(obj, dict):
        return {key: _convert_decimals(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals(value) for value in obj]
    return obj


def _convert_floats(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {key: _convert_floats(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_convert_floats(value) for value in obj]
    return obj


def get_session(session_id: str) -> dict:
    response = _get_table().get_item(Key={"sessionId": session_id})
    item = response.get("Item")
    if not item:
        raise KeyError("Session not found. Start a new session.")
    return _convert_decimals(item)


def save_session(item: dict) -> None:
    _get_table().put_item(Item=_convert_floats(item))


def update_session(session_id: str, key: str, value) -> None:
    _get_table().update_item(
        Key={"sessionId": session_id},
        UpdateExpression="SET #key = :value",
        ExpressionAttributeNames={"#key": key},
        ExpressionAttributeValues={":value": _convert_floats(value)},
    )


def save_service_config(session_id, service, config, provider=None):
    session = get_session(session_id)
    generated_config = session.get("generatedConfig", {})
    generated_config[service] = config
    configured_services = session.get("configuredServices", [])
    service_providers = session.get("serviceProviders", {})
    if service not in configured_services:
        configured_services.append(service)
    if provider:
        service_providers[service] = provider

    try:
        _get_table().update_item(
            Key={"sessionId": session_id},
            UpdateExpression="SET #generatedConfig.#service = :config, #configuredServices = :services, #serviceProviders = :serviceProviders",
            ExpressionAttributeNames={
                "#generatedConfig": "generatedConfig",
                "#service": service,
                "#configuredServices": "configuredServices",
                "#serviceProviders": "serviceProviders",
            },
            ExpressionAttributeValues={
                ":config": _convert_floats(config),
                ":services": configured_services,
                ":serviceProviders": service_providers,
            },
        )
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ValidationException":
            _get_table().update_item(
                Key={"sessionId": session_id},
                UpdateExpression="SET #generatedConfig = :generatedConfig, #configuredServices = :services, #serviceProviders = :serviceProviders",
                ExpressionAttributeNames={
                    "#generatedConfig": "generatedConfig",
                    "#configuredServices": "configuredServices",
                    "#serviceProviders": "serviceProviders",
                },
                ExpressionAttributeValues={
                    ":generatedConfig": _convert_floats(generated_config),
                    ":services": configured_services,
                    ":serviceProviders": service_providers,
                },
            )
        else:
            raise


def get_service_config(session_id, service) -> dict:
    return get_session(session_id).get("generatedConfig", {}).get(service, {})


def get_all_service_configs(session_id) -> dict:
    return get_session(session_id).get("generatedConfig", {})


def get_configured_services(session_id) -> list:
    return get_session(session_id).get("configuredServices", [])


def get_service_provider(session_id, service) -> str | None:
    return get_session(session_id).get("serviceProviders", {}).get(service)


def get_service_providers(session_id) -> dict:
    return get_session(session_id).get("serviceProviders", {})


def list_user_sessions(user_id: str) -> list[dict]:
    """Return summary rows for all sessions belonging to user_id, newest first."""
    table = _get_table()
    response = table.scan(
        FilterExpression=Attr("userId").eq(user_id),
        ProjectionExpression="sessionId, sessionTitle, createdAt, advisoryObjective",
    )
    items = [_convert_decimals(item) for item in response.get("Items", [])]
    return sorted(items, key=lambda x: x.get("createdAt", ""), reverse=True)
