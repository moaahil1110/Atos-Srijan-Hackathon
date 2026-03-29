from __future__ import annotations

import json
from typing import Any

from utils.local_retrieval import get_retriever
from utils.service_mapper import get_provider_label

DEFAULT_RETRIEVAL_TOP_K = 5

NIMBUS_SYSTEM_PROMPT = """
You are Nimbus, an expert cloud configuration advisor. Before making any
recommendation, optimization, or explanation, you must follow this strict
decision process in order:

STEP 1 - PROVIDER DOCUMENTATION FIRST
Read and fully understand the provider documentation chunks provided to
you in this prompt. These come from official Azure or GCP documentation.
Understand what the service does, what each field means, what values are
allowed, and what the provider recommends as secure and optimal defaults.

STEP 2 - COMPANY CONTEXT
Read the company description and profile. Understand the industry,
size, risk tolerance, cost sensitivity, and data sensitivity. Map the
company's needs against what you learned from the provider documentation
in Step 1.

STEP 3 - COMPLIANCE REQUIREMENTS
Read the compliance documentation chunks provided. These represent the
regulatory frameworks the company must follow (such as HIPAA, PCI-DSS,
SOC2, or others). Identify which compliance requirements apply to the
cloud service fields in question. If a compliance requirement conflicts
with a provider default, always prioritize the stricter compliance
requirement and flag the conflict explicitly.

STEP 4 - MAKE GROUNDED DECISIONS
Only after completing Steps 1, 2, and 3 should you produce your output.
Every field value you recommend or optimize must:
- Be supported by the provider documentation or compliance docs provided
- Include a brief citation of which source influenced the decision
- Be a specific, actionable value - not a vague suggestion
- Flag any conflict between provider defaults and compliance requirements
- If no relevant documentation was provided for a field, say so
  explicitly rather than guessing

WHAT YOU MUST NEVER DO:
- Make recommendations not grounded in the provided context
- Hallucinate field values or options not mentioned in the docs
- Access external information or APIs
- Skip the decision order above
- Give vague guidance when specific values are possible

In optimization mode, compare each current value against the provider
docs and compliance requirements. Explain what changed, what stayed the
same, and why.

In explanation mode, use the evidence already provided to explain past
decisions clearly and specifically.
""".strip()


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def build_company_context_query(company_profile: dict[str, Any]) -> str:
    parts = [
        _stringify(company_profile.get("industry")),
        ", ".join(company_profile.get("complianceFrameworks", []) or []),
        _stringify(company_profile.get("teamSize")),
        _stringify(company_profile.get("dataClassification")),
        _stringify(company_profile.get("weightReasoning")),
    ]
    return " ".join(part for part in parts if part) or "general compliance requirements"


def build_provider_query(
    service: str,
    field_names: list[str],
    current_config: dict[str, Any] | None = None,
) -> str:
    parts = [service, " ".join(field_names[:12])]
    if current_config:
        config_summary = " ".join(f"{key}={value}" for key, value in list(current_config.items())[:8])
        if config_summary:
            parts.append(config_summary)
    return " ".join(part for part in parts if part)


def retrieve_decision_evidence(
    company_profile: dict[str, Any],
    provider: str,
    service: str,
    field_names: list[str],
    current_config: dict[str, Any] | None = None,
    top_k: int = DEFAULT_RETRIEVAL_TOP_K,
) -> dict[str, list[dict[str, Any]]]:
    retriever = get_retriever()
    return {
        "compliance": retriever.retrieve(
            query=build_company_context_query(company_profile),
            source="compliance",
            top_k=top_k,
        ),
        "provider": retriever.retrieve(
            query=build_provider_query(service, field_names, current_config=current_config),
            source=provider,
            top_k=top_k,
        ),
    }


def retrieve_compliance_text(query: str, top_k: int = DEFAULT_RETRIEVAL_TOP_K) -> str:
    chunks = get_retriever().retrieve(query=query, source="compliance", top_k=top_k)
    return "\n\n".join(chunk["text"] for chunk in chunks)


def format_company_context(
    provider: str,
    service: str,
    company_profile: dict[str, Any],
    weights: dict[str, Any] | None = None,
) -> str:
    weights = weights or {}
    frameworks = ", ".join(company_profile.get("complianceFrameworks", []) or ["none"])
    lines = [
        f"Provider: {get_provider_label(provider)}",
        f"Service: {service}",
        f"Industry: {_stringify(company_profile.get('industry')) or 'not provided'}",
        f"Team / scale: {_stringify(company_profile.get('teamSize')) or 'not provided'}",
        f"Data classification: {_stringify(company_profile.get('dataClassification')) or 'not provided'}",
        f"Compliance frameworks: {frameworks}",
        f"Compliance maturity: {_stringify(company_profile.get('complianceMaturity')) or 'not provided'}",
        f"Risk tolerance: {_stringify(company_profile.get('riskTolerance')) or 'not provided'}",
        f"Cost pressure: {_stringify(company_profile.get('costPressure')) or 'not provided'}",
        f"Security weight: {_stringify(weights.get('security')) or 'not provided'}",
        f"Compliance weight: {_stringify(weights.get('compliance')) or 'not provided'}",
        f"Cost weight: {_stringify(weights.get('cost')) or 'not provided'}",
    ]
    return "\n".join(lines)


def format_chunk_block(title: str, chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return f"{title}\nNo relevant chunks were retrieved."

    sections = [title]
    for chunk in chunks:
        sections.append(
            f"Source: {chunk['source']} (chunk {chunk['chunk_index']})\n{chunk['text']}"
        )
    return "\n\n".join(sections)


def build_grounded_prompt(
    provider_chunks: list[dict[str, Any]],
    company_context: str,
    compliance_chunks: list[dict[str, Any]],
    task_instruction: str,
    output_instruction: str,
    current_config: dict[str, Any] | None = None,
) -> str:
    sections = [
        format_chunk_block("1. Provider Documentation Section", provider_chunks),
        f"2. Company Context Section\n{company_context}",
        format_chunk_block("3. Compliance Guidelines Section", compliance_chunks),
    ]
    if current_config is not None:
        sections.append(
            "4. Current Configuration Section\n"
            f"{json.dumps(current_config, indent=2, ensure_ascii=True)}"
        )
        sections.append(f"5. Task Instruction Section\n{task_instruction}")
        sections.append(f"6. Output Format Instruction\n{output_instruction}")
    else:
        sections.append(f"4. Task Instruction Section\n{task_instruction}")
        sections.append(f"5. Output Format Instruction\n{output_instruction}")
    return "\n\n".join(sections)
