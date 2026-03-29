from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.config import Config

from config import settings

logger = logging.getLogger(__name__)
_table = None


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_table():
    global _table
    if _table is None:
        resource_kwargs = {
            "region_name": settings.AWS_REGION,
            "config": Config(connect_timeout=1, read_timeout=2, retries={"max_attempts": 1}),
        }
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            resource_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            resource_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
        if settings.AWS_SESSION_TOKEN:
            resource_kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN
        _table = boto3.resource("dynamodb", **resource_kwargs).Table(settings.DYNAMO_TABLE)
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


def _ensure_defaults(item: dict) -> dict:
    now = _timestamp()
    created_at = item.get("createdAt") or now
    weights = item.get("weights") or item.get("computedWeights") or {}
    conversation_history = item.get("conversationHistory")
    if not isinstance(conversation_history, list):
        conversation_history = []

    default_item = {
        "sessionId": item.get("sessionId", ""),
        "companyProfile": item.get("companyProfile", {}),
        "weights": weights,
        "computedWeights": weights,
        "selectedProvider": item.get("selectedProvider", item.get("provider", "")),
        "selectedService": item.get("selectedService", ""),
        "currentConfig": item.get("currentConfig", {}),
        "generatedConfig": item.get("generatedConfig", {}),
        "decisionEvidence": item.get("decisionEvidence", {"compliance": [], "provider": []}),
        "decisionEvidenceByService": item.get("decisionEvidenceByService", {}),
        "conversationHistory": conversation_history,
        "fieldConversationHistory": item.get("fieldConversationHistory", {}),
        "terraformOutput": item.get("terraformOutput", ""),
        "createdAt": created_at,
        "updatedAt": now,
    }
    default_item.update(item)
    default_item["weights"] = default_item.get("weights") or default_item.get("computedWeights") or {}
    default_item["computedWeights"] = default_item["weights"]
    default_item["selectedProvider"] = default_item.get("selectedProvider") or default_item.get("provider", "")
    default_item["selectedService"] = default_item.get("selectedService") or ""
    default_item["decisionEvidence"] = default_item.get("decisionEvidence") or {"compliance": [], "provider": []}
    default_item["decisionEvidenceByService"] = default_item.get("decisionEvidenceByService") or {}
    default_item["currentConfig"] = default_item.get("currentConfig") or {}
    default_item["generatedConfig"] = default_item.get("generatedConfig") or {}
    default_item["conversationHistory"] = (
        default_item.get("conversationHistory")
        if isinstance(default_item.get("conversationHistory"), list)
        else []
    )
    default_item["fieldConversationHistory"] = (
        default_item.get("fieldConversationHistory")
        if isinstance(default_item.get("fieldConversationHistory"), dict)
        else {}
    )
    default_item["terraformOutput"] = default_item.get("terraformOutput") or ""
    default_item["createdAt"] = created_at
    default_item["updatedAt"] = now
    return default_item


def get_session(session_id: str) -> dict:
    response = _get_table().get_item(Key={"sessionId": session_id})
    item = response.get("Item")
    if not item:
        raise KeyError("Session not found. Start a new session.")
    return _ensure_defaults(_convert_decimals(item))


def save_session(item: dict) -> None:
    normalized = _ensure_defaults(item)
    _get_table().put_item(Item=_convert_floats(normalized))


def update_session_fields(session_id: str, updates: dict) -> dict:
    session = get_session(session_id)
    session.update(updates)
    save_session(session)
    return session


def update_session(session_id: str, key: str, value):
    return update_session_fields(session_id, {key: value})


def save_service_config(
    session_id,
    service,
    config,
    provider=None,
    decision_evidence: dict | None = None,
    current_config: dict | None = None,
):
    session = get_session(session_id)
    generated_config = session.get("generatedConfig", {})
    generated_config[service] = config

    configured_services = session.get("configuredServices", [])
    if service not in configured_services:
        configured_services.append(service)

    service_providers = session.get("serviceProviders", {})
    if provider:
        service_providers[service] = provider

    updates = {
        "generatedConfig": generated_config,
        "configuredServices": configured_services,
        "serviceProviders": service_providers,
        "selectedService": service,
        "selectedProvider": provider or session.get("selectedProvider", ""),
        "provider": provider or session.get("provider", ""),
    }

    if decision_evidence is not None:
        evidence_by_service = session.get("decisionEvidenceByService", {})
        evidence_by_service[service] = decision_evidence
        updates["decisionEvidence"] = decision_evidence
        updates["decisionEvidenceByService"] = evidence_by_service

    if current_config is not None:
        updates["currentConfig"] = current_config

    update_session_fields(session_id, updates)


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
    table = _get_table()
    response = table.scan(
        FilterExpression=Attr("userId").eq(user_id),
        ProjectionExpression="sessionId, sessionTitle, createdAt, updatedAt, advisoryObjective",
    )
    items = [_ensure_defaults(_convert_decimals(item)) for item in response.get("Items", [])]
    return sorted(items, key=lambda x: x.get("updatedAt", ""), reverse=True)
