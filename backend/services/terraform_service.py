import json
import logging

from fastapi import HTTPException

from utils.bedrock_client import invoke_bedrock
from utils.dynamo_client import (
    get_all_service_configs,
    get_service_config,
    get_service_provider,
    get_service_providers,
    get_session,
    update_session_fields,
)
from utils.grounding import (
    DEFAULT_RETRIEVAL_TOP_K,
    NIMBUS_SYSTEM_PROMPT,
    build_grounded_prompt,
    format_company_context,
    retrieve_decision_evidence,
)
from utils.service_mapper import (
    get_provider_label,
    get_provider_service_name,
    get_terraform_resources,
    normalize_provider,
)

logger = logging.getLogger(__name__)

TERRAFORM_OUTPUT_INSTRUCTION = """
Return ONLY valid Terraform HCL.
- No markdown fences
- No prose before or after the HCL
- Use inline comments where helpful to preserve grounded reasoning
""".strip()

PROVIDER_VERSIONS = {
    "aws": ("aws", "hashicorp/aws", "5.0"),
    "azure": ("azurerm", "hashicorp/azurerm", "3.0"),
    "gcp": ("google", "hashicorp/google", "5.0"),
}


def _weights(session: dict) -> dict:
    return session.get("weights") or session.get("computedWeights") or {}


def _normalize_config(raw_config: dict) -> tuple[dict, dict]:
    values = {}
    reasons = {}
    for field_id, entry in raw_config.items():
        if isinstance(entry, dict) and "value" in entry:
            values[field_id] = entry["value"]
            reasons[field_id] = entry.get("reason", "")
        else:
            values[field_id] = entry
            reasons[field_id] = ""
    return values, reasons


def _provider_block(provider: str) -> list[str]:
    provider = normalize_provider(provider)
    name, source, version = PROVIDER_VERSIONS.get(provider, ("aws", "hashicorp/aws", "5.0"))
    terraform_lines = [
        "terraform {",
        '  required_version = ">= 1.5"',
        "  required_providers {",
        f"    {name} = {{",
        f'      source  = "{source}"',
        f'      version = "~> {version}"',
        "    }",
        "  }",
        "}",
    ]
    if provider == "azure":
        return terraform_lines + ['provider "azurerm" {', "  features {}", "}"]
    if provider == "gcp":
        return terraform_lines + ['provider "google" {', "  project = var.gcp_project", "  region = var.gcp_region", "}"]
    return terraform_lines + ['provider "aws" {', "  region = var.aws_region", "}"]


def _strip_markdown_fences(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1]).strip()
    return cleaned


def _build_evidence_context(session: dict, service_name: str, provider: str, values: dict) -> tuple[list[dict], list[dict]]:
    evidence_by_service = session.get("decisionEvidenceByService", {})
    saved = evidence_by_service.get(service_name)
    if saved and saved.get("provider") and saved.get("compliance"):
        return saved["provider"], saved["compliance"]

    refreshed = retrieve_decision_evidence(
        company_profile=session.get("companyProfile", {}),
        provider=provider,
        service=service_name,
        field_names=list(values.keys()),
        current_config=values,
        top_k=DEFAULT_RETRIEVAL_TOP_K,
    )
    return refreshed["provider"], refreshed["compliance"]


async def generate_terraform(session_id, service=None, provider="aws") -> str:
    provider = normalize_provider(provider)
    try:
        session = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")

    if service:
        canonical_service = get_provider_service_name(service, provider)
        raw_config = get_service_config(session_id, canonical_service)
        if not raw_config:
            raise HTTPException(
                status_code=400,
                detail=f"No config found for {canonical_service}. Generate config first.",
            )
        raw_configs = {canonical_service: raw_config}
        service_provider_map = {canonical_service: get_service_provider(session_id, canonical_service) or provider}
    else:
        raw_configs = get_all_service_configs(session_id)
        if not raw_configs:
            raise HTTPException(status_code=400, detail="No configured services found. Generate config first.")
        service_provider_map = get_service_providers(session_id) or {}

    normalized_configs = {}
    for current_service, raw_service_config in raw_configs.items():
        values, reasons = _normalize_config(raw_service_config)
        if not values:
            raise ValueError(
                f"Generated config for {current_service} has no field values. Regenerate the config before exporting Terraform."
            )
        current_provider = service_provider_map.get(current_service, provider)
        provider_chunks, compliance_chunks = _build_evidence_context(session, current_service, current_provider, values)
        normalized_configs[current_service] = {
            "provider": current_provider,
            "values": values,
            "reasons": reasons,
            "provider_chunks": provider_chunks,
            "compliance_chunks": compliance_chunks,
        }

    company_profile = session.get("companyProfile", {})
    weights = _weights(session)

    if len(normalized_configs) == 1:
        current_service, payload = next(iter(normalized_configs.items()))
        task_instruction = f"""
Generate production-ready Terraform for {get_provider_label(payload['provider'])} {current_service}.

Resource type mappings:
{json.dumps(get_terraform_resources(current_service, payload['provider']), indent=2, ensure_ascii=True)}

Configuration values to implement:
{json.dumps(payload['values'], indent=2, ensure_ascii=True)}

Field reasons to preserve as comments:
{json.dumps(payload['reasons'], indent=2, ensure_ascii=True)}

Required provider block:
{chr(10).join(_provider_block(payload['provider']))}
""".strip()
        prompt = build_grounded_prompt(
            provider_chunks=payload["provider_chunks"],
            company_context=format_company_context(payload["provider"], current_service, company_profile, weights),
            compliance_chunks=payload["compliance_chunks"],
            task_instruction=task_instruction,
            output_instruction=TERRAFORM_OUTPUT_INSTRUCTION,
        )
        content = invoke_bedrock(prompt, system=NIMBUS_SYSTEM_PROMPT, max_tokens=2200, temperature=0.1)
    else:
        provider_chunks = []
        compliance_chunks = []
        multi_service_payload = {}
        for current_service, payload in normalized_configs.items():
            provider_chunks.extend(payload["provider_chunks"])
            compliance_chunks.extend(payload["compliance_chunks"])
            multi_service_payload[current_service] = {
                "provider": payload["provider"],
                "resources": get_terraform_resources(current_service, payload["provider"]),
                "values": payload["values"],
                "reasons": payload["reasons"],
            }

        task_instruction = f"""
Generate a multi-service Terraform configuration.

Services to include:
{json.dumps(multi_service_payload, indent=2, ensure_ascii=True)}

Provider blocks to include:
{json.dumps({provider_name: _provider_block(provider_name) for provider_name in sorted({payload['provider'] for payload in normalized_configs.values()})}, indent=2, ensure_ascii=True)}
""".strip()
        prompt = build_grounded_prompt(
            provider_chunks=provider_chunks,
            company_context=format_company_context("multi", "multiple services", company_profile, weights),
            compliance_chunks=compliance_chunks,
            task_instruction=task_instruction,
            output_instruction=TERRAFORM_OUTPUT_INSTRUCTION,
        )
        content = invoke_bedrock(prompt, system=NIMBUS_SYSTEM_PROMPT, max_tokens=3200, temperature=0.1)

    cleaned = _strip_markdown_fences(content)
    if "resource" not in cleaned:
        raise ValueError("Terraform generation did not return valid resource blocks.")

    update_session_fields(
        session_id,
        {
            "terraformOutput": cleaned,
            "selectedProvider": provider,
            "selectedService": service or "ALL",
        },
    )
    return cleaned
