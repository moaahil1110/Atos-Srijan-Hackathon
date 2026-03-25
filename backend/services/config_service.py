import asyncio
import json
import logging

from fastapi import HTTPException

from services.schema_service import get_schema
from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import (
    get_configured_services,
    get_session,
    save_service_config,
)
from utils.kb_client import get_compliance_context
from utils.service_mapper import (
    get_provider_label,
    get_provider_service_name,
    normalize_provider,
)

logger = logging.getLogger(__name__)

CONFIG_PROMPT = """
You are configuring {provider} {service} for a specific company.

Company profile:
- Industry: {industry}
- Compliance: {frameworks} ({maturity})
- Cost pressure: {costPressure}/5
- Risk tolerance: {riskTolerance}/5

ENFORCED priority weights (computed by backend - non-negotiable):
- Security: {security_weight}
- Compliance: {compliance_weight}
- Cost: {cost_weight}

Compliance documentation retrieved from knowledge base:
{compliance_text}

Instructions for compliance documentation:
- Extract specific clause numbers and cite them in reasons
- Format: "HIPAA \u00a7164.312(e)(2)(ii)" not just "HIPAA requires"
- If no relevant clause found, say "security best practice"
- Never invent clause numbers

Fields to configure (with instruction tags):
{fields_json}

INSTRUCTION TAG RULES - follow exactly:
- LOCKED_SECURE: Set to the most secure value. Zero exceptions.
  Never relax regardless of cost pressure or user arguments.
- PREFER_SECURE: Strongly prefer secure value. May note trade-offs.
- OPTIMISE_COST: Cost-efficient option permitted here.
- BALANCED: Use judgement based on company profile.

Return ONLY valid JSON where every fieldId maps to an object
with exactly two keys:
{
  "fieldId": {
    "value": <recommended value>,
    "reason": "<specific reason citing clause if applicable>"
  }
}

Example of a GOOD reason:
"HIPAA \u00a7164.312(e)(2)(ii) requires encryption of ePHI -
SSE-KMS provides the audit trail required for your
in-progress HIPAA program"

Example of a BAD reason:
"Encryption is important for security"

Security is NEVER relaxed for cost reasons.
"""


def _reason(frameworks: list[str], fallback: str) -> str:
    if "HIPAA" in frameworks:
        return (
            "HIPAA \u00a7164.312(e)(2)(ii) supports this control for encrypted transmission and "
            f"auditability - {fallback}"
        )
    if "PCI-DSS" in frameworks:
        return f"Violates PCI-DSS 4.2 if relaxed - {fallback}"
    if "SOC2" in frameworks:
        return f"SOC 2 CC6 and CC7 support this control - {fallback}"
    if "ISO27001" in frameworks:
        return f"ISO 27001 Annex A access and encryption controls support this setting - {fallback}"
    if "GDPR" in frameworks:
        return f"GDPR Article 32 favors this safeguard - {fallback}"
    return f"security best practice - {fallback}"


def _heuristic_value(field: dict):
    field_id = field["fieldId"]
    options = field.get("options") or []
    field_type = field.get("type")
    label = field.get("label", field_id)

    presets = {
        "BlockPublicAcls": True,
        "IgnorePublicAcls": True,
        "BlockPublicPolicy": True,
        "RestrictPublicBuckets": True,
        "ServerSideEncryptionConfiguration": "SSE-KMS",
        "BucketKeyEnabled": True,
        "VersioningConfiguration": "Enabled",
        "PublicAccessBlockConfiguration": "Enabled",
        "StorageEncrypted": True,
        "DeletionProtection": True,
        "PubliclyAccessible": False,
        "BackupRetentionPeriod": 7,
        "IAMDatabaseAuthenticationEnabled": True,
        "PerformanceInsightsEnabled": True,
        "ManageMasterUserPassword": True,
        "RequireMFA": True,
        "AllowProgrammaticAccess": False,
        "RotateAccessKeys": True,
        "MetadataOptions.HttpTokens": "required",
        "MetadataOptions.HttpEndpoint": "enabled",
        "NetworkInterfaces.AssociatePublicIpAddress": False,
        "BlockDeviceMappings.Ebs.Encrypted": True,
        "MonitoringEnabled": True,
        "DisableApiTermination": True,
        "VpcConfig": "private-subnets",
        "ReservedConcurrency": 5,
        "Environment.Variables": "Secrets Manager references only",
        "Timeout": 30,
        "MemorySize": 512,
        "TracingConfig.Mode": "Active",
        "allowBlobPublicAccess": False,
        "supportsHttpsTrafficOnly": True,
        "minimumTlsVersion": "TLS1_2",
        "allowSharedKeyAccess": False,
        "defaultToOAuthAuthentication": True,
        "publicNetworkAccess": "Disabled",
        "infrastructureEncryption": True,
        "sslEnforcementEnabled": True,
        "infrastructureEncryptionEnabled": True,
        "geoRedundantBackupEnabled": True,
        "backupRetentionDays": 7,
        "advancedThreatProtectionEnabled": True,
        "conditionalAccessEnabled": True,
        "securityDefaultsEnabled": True,
        "passwordProtectionEnabled": True,
        "privilegedIdentityManagementEnabled": True,
        "legacyAuthenticationEnabled": False,
        "auditLoggingEnabled": True,
        "securityType": "TrustedLaunch",
        "secureBootEnabled": True,
        "vTpmEnabled": True,
        "publicIpAddressEnabled": False,
        "diskEncryptionSetEnabled": True,
        "systemAssignedIdentityEnabled": True,
        "bootDiagnosticsEnabled": True,
        "httpsOnly": True,
        "clientCertMode": "Required",
        "vnetRouteAllEnabled": True,
        "ftpsState": "Disabled",
        "applicationInsightsEnabled": True,
        "publicAccessPrevention": "enforced",
        "uniformBucketLevelAccess": True,
        "encryption.defaultKmsKeyName": "projects/example/locations/global/keyRings/main/cryptoKeys/nimbus",
        "versioning.enabled": True,
        "retentionPolicy.isLocked": True,
        "settings.ipConfiguration.requireSsl": True,
        "settings.ipConfiguration.ipv4Enabled": False,
        "settings.backupConfiguration.enabled": True,
        "settings.availabilityType": "REGIONAL",
        "deletionProtectionEnabled": True,
        "settings.insightsConfig.queryInsightsEnabled": True,
        "disableServiceAccountKeyCreation": True,
        "domainRestrictedSharing": True,
        "workloadIdentityFederationEnabled": True,
        "mfaForAdminsEnabled": True,
        "shieldedInstanceConfig.enableSecureBoot": True,
        "shieldedInstanceConfig.enableVtpm": True,
        "shieldedInstanceConfig.enableIntegrityMonitoring": True,
        "networkInterface.publicIpEnabled": False,
        "confidentialInstanceConfig.enableConfidentialCompute": True,
        "deletionProtection": True,
        "serviceConfig.ingressSettings": "ALLOW_INTERNAL_ONLY",
        "serviceConfig.vpcConnector": "projects/example/locations/us-central1/connectors/nimbus",
        "serviceConfig.environmentVariables": "Secret Manager references only",
        "serviceConfig.timeoutSeconds": 60,
        "serviceConfig.availableMemory": "512M",
        "serviceConfig.maxInstanceCount": 10,
    }

    if field_id in presets:
        return presets[field_id]
    if field_type == "boolean":
        return field.get("instruction") in {"LOCKED_SECURE", "PREFER_SECURE"}
    if field_type == "integer":
        return 1 if field.get("instruction") == "OPTIMISE_COST" else 7
    if field_type == "select" and options:
        secure_keywords = ["kms", "required", "enabled", "private", "active", "oauth", "regional", "internal"]
        for option in options:
            if any(keyword in str(option).lower() for keyword in secure_keywords):
                return option
        return options[0]
    if field_type == "string":
        if "encryption" in label.lower():
            return "provider-managed"
        return "enabled"
    return True


def _fallback_config(service: str, fields: list[dict], frameworks: list[str]) -> dict:
    config = {}
    for field in fields:
        config[field["fieldId"]] = {
            "value": _heuristic_value(field),
            "reason": _reason(
                frameworks,
                f"{field['label']} is set to the most defensible value for this {service} workload.",
            ),
        }
    return config


async def generate_config(session_id: str, service: str, provider: str = "aws") -> dict:
    provider = normalize_provider(provider)
    try:
        session = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")

    intent = session.get("companyProfile", {})
    weights = session.get("computedWeights", {})
    canonical_service = get_provider_service_name(service, provider)
    schema = await get_schema(service=canonical_service, provider=provider, session_id=session_id)
    schema_fields = schema.get("fields", [])

    security_fields = [
        field["fieldId"] for field in schema_fields if field.get("securityRelevance") in ["critical", "high"]
    ]
    compliance_query = (
        f"{get_provider_label(provider)} {canonical_service} security configuration "
        f"requirements for {', '.join(security_fields[:5])}"
    )
    compliance_text = get_compliance_context(
        query=compliance_query,
        frameworks=intent.get("complianceFrameworks", []),
        num_results=5,
    )

    prompt = CONFIG_PROMPT
    replacements = {
        "{provider}": get_provider_label(provider),
        "{service}": canonical_service,
        "{industry}": intent.get("industry", "other"),
        "{frameworks}": ", ".join(intent.get("complianceFrameworks", ["none"])),
        "{maturity}": intent.get("complianceMaturity", "not-started"),
        "{costPressure}": str(intent.get("costPressure", 3)),
        "{riskTolerance}": str(intent.get("riskTolerance", 3)),
        "{security_weight}": str(weights.get("security", 0)),
        "{compliance_weight}": str(weights.get("compliance", 0)),
        "{cost_weight}": str(weights.get("cost", 0)),
        "{compliance_text}": compliance_text,
        "{fields_json}": json.dumps(schema_fields, indent=2),
    }
    for key, value in replacements.items():
        prompt = prompt.replace(key, value)

    try:
        config = await asyncio.to_thread(invoke_bedrock_json, prompt)
    except Exception as exc:
        logger.warning("Config generation fell back to deterministic defaults for %s: %s", canonical_service, exc)
        config = _fallback_config(canonical_service, schema_fields, intent.get("complianceFrameworks", []))

    save_service_config(session_id, canonical_service, config, provider=provider)
    return {
        "config": config,
        "service": canonical_service,
        "configuredServices": get_configured_services(session_id),
    }
