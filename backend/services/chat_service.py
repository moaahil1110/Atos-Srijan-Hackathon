import logging
import re
import uuid
from datetime import datetime, timezone

from services.weights_engine import compute_weights
from utils.bedrock_client import invoke_bedrock, invoke_bedrock_json
from utils.dynamo_client import get_session, save_session, update_session, update_session_fields
from utils.grounding import DEFAULT_RETRIEVAL_TOP_K, NIMBUS_SYSTEM_PROMPT, retrieve_compliance_text
from utils.service_mapper import get_provider_label, get_provider_service_name, get_provider_services

logger = logging.getLogger(__name__)

CONTEXT_KEYS = (
    "industry",
    "workload_type",
    "scale",
    "budget",
    "compliance",
    "security_level",
    "current_stack",
)

OBJECTIVE_META = {
    "recommendation": {
        "label": "Recommendation",
        "prompt": "The user wants the best-fit cloud recommendation with clear reasoning.",
        "follow_up": "Keep discovery focused on what is needed to recommend the best provider and service mix.",
        "ready": "I now have enough context to recommend the strongest-fit cloud plan.",
    },
    "optimize": {
        "label": "Optimise",
        "prompt": "The user wants an optimisation-ready target architecture that can be compared against an existing setup.",
        "follow_up": "Keep discovery focused on what is needed to build a target architecture for optimisation and comparison.",
        "ready": "I now have enough context to prepare the target architecture for optimisation.",
    },
    "terraform": {
        "label": "Terraform",
        "prompt": "The user wants a Terraform-ready architecture and implementation-oriented output.",
        "follow_up": "Keep discovery focused on what is needed to build a Terraform-ready target architecture.",
        "ready": "I now have enough context to prepare a Terraform-ready cloud plan.",
    },
}


def _normalize_objective(objective: str | None) -> str:
    value = _normalize_text(objective or "")
    return value if value in OBJECTIVE_META else "recommendation"


def _initial_session(session_id: str, objective: str = "recommendation", user_id: str = "") -> dict:
    normalized_objective = _normalize_objective(objective)
    return {
        "sessionId": session_id,
        "userId": user_id,
        "sessionTitle": "",
        "companyProfile": {},
        "weights": {},
        "computedWeights": {},
        "selectedProvider": "multi",
        "selectedService": "",
        "currentConfig": {},
        "generatedConfig": {},
        "decisionEvidence": {"compliance": [], "provider": []},
        "decisionEvidenceByService": {},
        "configuredServices": [],
        "suggestedServices": [],
        "provider": "multi",
        "serviceProviders": {},
        "conversationHistory": [],
        "fieldConversationHistory": {},
        "terraformOutput": "",
        "advisoryConversation": [],
        "advisoryContext": {},
        "advisorRecommendations": [],
        "advisorReasoningMode": "bedrock-model",
        "advisoryObjective": normalized_objective,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def _normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def _as_text(value) -> str:
    return "" if value is None else str(value).strip()


def _conversation_text(conversation: list[dict]) -> str:
    lines = []
    for message in conversation:
        role = "Assistant" if message.get("role") == "assistant" else "User"
        content = _as_text(message.get("content"))
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _clean_context(candidate: dict, existing: dict | None = None) -> dict:
    merged = dict(existing or {})
    for key in CONTEXT_KEYS:
        value = _as_text(candidate.get(key))
        if value:
            merged[key] = value
    return merged


def _coverage(context: dict) -> dict[str, bool]:
    return {
        "business": bool(context.get("industry") or context.get("workload_type")),
        "scale": bool(context.get("scale")),
        "security": bool(context.get("compliance") or context.get("security_level")),
        "cost": bool(context.get("budget")),
    }


def _parse_frameworks(compliance: str | None) -> list[str]:
    if not compliance:
        return ["none"]
    frameworks = []
    normalized = compliance.lower().replace("-", "")
    for framework in ["HIPAA", "PCI-DSS", "SOC2", "ISO27001", "GDPR"]:
        if framework.lower().replace("-", "") in normalized:
            frameworks.append(framework)
    return frameworks or ["none"]


def _parse_maturity(compliance: str | None) -> str:
    text = _normalize_text(compliance or "")
    if "certified" in text:
        return "certified"
    if "in progress" in text or "in-progress" in text:
        return "in-progress"
    if "not started" in text or "not-started" in text:
        return "not-started"
    return "not-started"


def _context_to_profile(context: dict) -> dict:
    frameworks = _parse_frameworks(context.get("compliance"))
    risk_tolerance = 1 if frameworks != ["none"] or _normalize_text(context.get("security_level", "")) == "high" else 3
    cost_pressure = 4 if "cost" in _normalize_text(context.get("budget", "")) or "budget" in _normalize_text(context.get("budget", "")) else 2
    data_classification = "highly-confidential" if "HIPAA" in frameworks or context.get("industry") == "healthcare" else "confidential" if frameworks != ["none"] else "internal"
    return {
        "industry": context.get("industry", "other"),
        "complianceFrameworks": frameworks,
        "complianceMaturity": _parse_maturity(context.get("compliance")),
        "teamSize": context.get("scale", "growing workload"),
        "costPressure": cost_pressure,
        "riskTolerance": risk_tolerance,
        "missionCriticalServices": [context.get("workload_type", "core workload")],
        "dataClassification": data_classification,
        "weightReasoning": "Weights are driven by discovered security, compliance, and budget signals from the advisory conversation.",
    }


def _matched_requirements(context: dict) -> list[str]:
    matches = []
    for key, label in [
        ("industry", "Industry"),
        ("workload_type", "Workload"),
        ("scale", "Scale"),
        ("compliance", "Compliance"),
        ("budget", "Budget"),
        ("security_level", "Security"),
        ("current_stack", "Current stack"),
    ]:
        value = context.get(key)
        if value:
            matches.append(f"{label}: {value}")
    return matches


def _extract_citations(compliance_text: str) -> list[str]:
    patterns = [
        r"HIPAA\s§\s?\d+\.\d+(?:\([^)]+\))*",
        r"HIPAA\sSection\s\d+\.\d+(?:\([^)]+\))*",
        r"PCI-DSS\s\d+(?:\.\d+)+",
        r"SOC\s?2\s[A-Z0-9.]+",
        r"GDPR\sArticle\s\d+",
    ]
    citations = []
    for pattern in patterns:
        for match in re.findall(pattern, compliance_text or "", flags=re.IGNORECASE):
            cleaned = re.sub(r"\s+", " ", match).strip()
            if cleaned not in citations:
                citations.append(cleaned)
    return citations[:4]


def _extract_evidence(compliance_text: str) -> list[str]:
    text = re.sub(r"\s+", " ", compliance_text or "").strip()
    evidence = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if sentence and any(token in sentence.lower() for token in ["hipaa", "pci", "soc", "gdpr", "encryption", "access", "audit"]):
            evidence.append(sentence[:240])
        if len(evidence) == 4:
            break
    return evidence


def _normalize_provider(provider: str) -> str:
    value = _normalize_text(provider)
    if value in {"aws", "amazon web services"}:
        return "aws"
    if value in {"azure", "microsoft azure"}:
        return "azure"
    if value in {"gcp", "google cloud", "google cloud platform"}:
        return "gcp"
    return "aws"


def _normalize_options(raw_options: list[dict], context: dict, citations: list[str], evidence: list[str]) -> list[dict]:
    normalized = []
    trace = _matched_requirements(context)
    for index, option in enumerate(raw_options or [], start=1):
        providers = []
        for block in option.get("providers", []):
            provider = _normalize_provider(block.get("provider", "aws"))
            services = []
            for item in block.get("services", []):
                service_name = get_provider_service_name(_as_text(item.get("service")) or get_provider_services(provider)[0], provider)
                requirement_matches = item.get("requirementMatches") or trace[:4]
                services.append(
                    {
                        "service": service_name,
                        "reason": _as_text(item.get("reason")) or f"{service_name} fits the discovered workload and control requirements.",
                        "detailedReason": _as_text(item.get("detailedReason")) or f"{service_name} was selected because it directly supports the stated workload, security posture, and operating constraints for this architecture.",
                        "requirementMatches": requirement_matches,
                        "userRequirementTrace": requirement_matches,
                        "complianceEvidence": evidence[:2],
                        "citations": citations,
                    }
                )
            if not services:
                continue
            providers.append(
                {
                    "provider": provider,
                    "role": _as_text(block.get("role")) or "Primary cloud",
                    "reason": _as_text(block.get("reason")) or f"{get_provider_label(provider)} is a strong fit for the stated workload and constraints.",
                    "detailedReason": _as_text(block.get("detailedReason")) or f"Nimbus matched {get_provider_label(provider)} to the user's industry, workload pattern, compliance posture, and budget signals rather than relying on a generic provider default.",
                    "complianceEvidence": evidence[:2],
                    "userRequirementTrace": trace,
                    "services": services,
                }
            )
        if not providers:
            continue
        mode = "hybrid" if len(providers) > 1 else "single-cloud"
        fit_score = option.get("fitScore", 82)
        try:
            fit_score = int(float(fit_score))
        except (TypeError, ValueError):
            fit_score = 82
        normalized.append(
            {
                "optionId": _as_text(option.get("optionId")) or f"option-{index}",
                "title": _as_text(option.get("title")) or ("Hybrid fit" if mode == "hybrid" else f"Best single-cloud fit: {get_provider_label(providers[0]['provider'])}"),
                "mode": mode,
                "fitScore": max(60, min(99, fit_score)),
                "summary": _as_text(option.get("summary")) or providers[0]["reason"],
                "detailedExplanation": _as_text(option.get("detailedExplanation")) or providers[0]["detailedReason"],
                "tradeoffs": _as_text(option.get("tradeoffs")) or "This option improves fit, but you should weigh specialization against operational simplicity.",
                "matchedRequirements": option.get("matchedRequirements") or trace,
                "providers": providers,
                "explainability": {
                    "noveltyNote": "Nimbus ties every provider and service recommendation back to both the user's stated requirements and retrieved compliance evidence, which makes the reasoning inspectable instead of generic.",
                    "userRequirementTrace": trace,
                    "complianceEvidence": evidence,
                    "citations": citations,
                },
            }
        )
    return sorted(normalized, key=lambda item: item["fitScore"], reverse=True)[:3]

def _model_extract_context(conversation: list[dict], existing_context: dict, objective: str) -> tuple[dict, dict[str, bool], bool, str, str]:
    objective_meta = OBJECTIVE_META[_normalize_objective(objective)]
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Nimbus, a senior multi-cloud security architect. Your only job is to extract context from the conversation transcript and return a JSON object. Do NOT recommend cloud providers or services. Do NOT answer the user's questions. ONLY extract and return JSON.
<|eot_id|><|start_header_id|>user<|end_header_id|>

Advisory objective: {objective_meta['label']} — {objective_meta['prompt']}

Existing captured context (preserve all values, only update if transcript changes them):
{existing_context}

Conversation transcript:
{_conversation_text(conversation)}

Extract or update the fields from the transcript. Include ONLY information explicitly stated by the user.

Return ONLY this JSON object — no markdown, no explanation, no extra text:
{{
  "industry": "e.g. healthcare, fintech, ecommerce, saas — or empty string",
  "workload_type": "e.g. api backend, web app, data platform, ml platform — or empty string",
  "scale": "e.g. 50k users, 1M requests/day, 10 TB data — or empty string",
  "budget": "e.g. cost sensitive, startup budget, enterprise, flexible — or empty string",
  "compliance": "e.g. HIPAA, PCI-DSS, SOC2, GDPR, ISO27001 — or empty string",
  "security_level": "e.g. high, medium, standard — or empty string",
  "current_stack": "e.g. AWS, Microsoft 365, on-premise Oracle — or empty string",
  "context_coverage": {{
    "business": true if industry or workload_type is known else false,
    "scale": true if scale is known else false,
    "security": true if compliance or security_level is known else false,
    "cost": true if budget is known else false
  }},
  "sufficient_context": true only if ALL four context_coverage values are true,
  "prepared_summary": "1-2 factual sentences summarising what is known, grounded only in the conversation",
  "follow_up_question": "one specific question to fill the first missing coverage area — empty string if sufficient_context is true"
}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
""".strip()
    result = invoke_bedrock_json(prompt, system=NIMBUS_SYSTEM_PROMPT)
    context = _clean_context(result, existing_context)
    coverage = result.get("context_coverage") or _coverage(context)
    normalized_coverage = {
        "business": bool(coverage.get("business")),
        "scale": bool(coverage.get("scale")),
        "security": bool(coverage.get("security")),
        "cost": bool(coverage.get("cost")),
    }
    sufficient_context = all(normalized_coverage.values())
    prepared_summary = _as_text(result.get("prepared_summary")) or ", ".join(_matched_requirements(context)[:4])
    follow_up_question = _as_text(result.get("follow_up_question"))
    return context, normalized_coverage, sufficient_context, prepared_summary, follow_up_question


def _model_build_options(context: dict, objective: str) -> list[dict]:
    objective_key = _normalize_objective(objective)
    objective_meta = OBJECTIVE_META[objective_key]
    compliance_text = retrieve_compliance_text(
        f"Best cloud architecture for {context.get('industry', 'regulated')} {context.get('workload_type', 'application')} with {context.get('compliance', 'security controls')}",
        top_k=DEFAULT_RETRIEVAL_TOP_K,
    )
    citations = _extract_citations(compliance_text)
    evidence = _extract_evidence(compliance_text)
    allowed_catalog = {
        "aws": get_provider_services("aws"),
        "azure": get_provider_services("azure"),
        "gcp": get_provider_services("gcp"),
    }
    requirement_trace = _matched_requirements(context)
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Nimbus, an expert multi-cloud security architect. You are generating a ranked list of cloud architecture recommendations.
Return ONLY a valid JSON array. No explanation, no markdown, no text before or after the JSON.
<|eot_id|><|start_header_id|>user<|end_header_id|>

Advisory objective: {objective_meta['label']} — {objective_meta['prompt']}

User requirements captured during discovery:
{chr(10).join(f'  - {r}' for r in requirement_trace)}

Compliance documentation (use this to justify recommendations, never invent clause numbers):
{compliance_text[:2000]}

Allowed cloud services catalog (ONLY use services from this list):
  AWS: {', '.join(allowed_catalog['aws'])}
  Azure: {', '.join(allowed_catalog['azure'])}
  GCP: {', '.join(allowed_catalog['gcp'])}

Generate up to 3 ranked architecture options. The first must be the STRONGEST fit — not the most popular choice.
You may mix providers in a single option if it genuinely fits best (hybrid).

Rules:
- Every provider and service reason MUST reference the user's specific requirements above.
- Never invent compliance clause numbers — only cite what is in the compliance documentation.
- fitScore must be between 60 and 99.
- Use only service names from the allowed catalog.
- If objective is Optimise: frame options as the ideal target state for comparison against an existing setup.
- If objective is Terraform: prefer services with clean Terraform provider support and mention deploy-readiness.

Return ONLY this JSON array:
[
  {{
    "optionId": "unique-short-id",
    "title": "Short descriptive title",
    "fitScore": 91,
    "summary": "2–3 sentence summary tying the option to the user's requirements",
    "detailedExplanation": "Detailed explanation referencing industry, scale, compliance, and budget signals",
    "tradeoffs": "What the user gives up or must consider with this option",
    "matchedRequirements": ["list of matched requirement strings"],
    "providers": [
      {{
        "provider": "aws|azure|gcp",
        "role": "e.g. Primary cloud, Identity & compliance layer",
        "reason": "Why this provider fits — tie to user requirements",
        "detailedReason": "Expanded explanation with compliance and workload justification",
        "services": [
          {{
            "service": "exact service name from the allowed catalog",
            "reason": "Why this service — tie to a specific user requirement",
            "detailedReason": "Expanded service justification with compliance linkage",
            "requirementMatches": ["specific requirement this service addresses"]
          }}
        ]
      }}
    ]
  }}
]
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
""".strip()
    raw_options = invoke_bedrock_json(prompt, system=NIMBUS_SYSTEM_PROMPT)
    if isinstance(raw_options, dict):
        raw_options = raw_options.get("options", [])
    normalized = _normalize_options(raw_options, context, citations, evidence)
    if not normalized:
        raise ValueError("Model returned no valid architecture options.")
    return normalized


def _model_ready_reply(context: dict, best_option: dict, objective: str) -> str:
    objective_meta = OBJECTIVE_META[_normalize_objective(objective)]
    industry = context.get('industry', 'your domain')
    frameworks = ', '.join(_parse_frameworks(context.get('compliance')))
    top_provider = best_option.get('providers', [{}])[0].get('provider', 'cloud').upper()
    fit_score = best_option.get('fitScore', '')
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Nimbus, a cloud architecture advisor. Write a concise, confident reply to the user. Plain text only — no markdown, no bullet points, no headers.
<|eot_id|><|start_header_id|>user<|end_header_id|>

The discovery interview is complete. Write a 3–4 sentence reply that:
1. Confirms you have captured enough context for the objective: {objective_meta['label']}.
2. Names the strongest recommendation ({top_provider}, fit score {fit_score}) and why it fits {industry} with {frameworks} compliance requirements.
3. Tells the user the architecture options are shown below with full requirement tracing and compliance evidence.
4. Invites them to load a recommendation into the Configuration Lab or ask follow-up questions.

Do NOT use bullet points or headers. Write as flowing sentences. Maximum 4 sentences.
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
""".strip()
    return invoke_bedrock(prompt, system=NIMBUS_SYSTEM_PROMPT, temperature=0.3, max_tokens=300).strip()


async def process_chat(session_id: str | None, user_message: str, objective: str = "recommendation", user_id: str = "") -> dict:
    current_objective = _normalize_objective(objective)
    if not session_id:
        session_id = str(uuid.uuid4())
        session_item = _initial_session(session_id, current_objective, user_id)
        save_session(session_item)
    else:
        try:
            session_item = get_session(session_id)
        except KeyError:
            session_item = _initial_session(session_id, current_objective, user_id)
            save_session(session_item)
        else:
            current_objective = _normalize_objective(objective or session_item.get("advisoryObjective"))

    advisory_conversation = session_item.get("advisoryConversation", [])
    advisory_context = session_item.get("advisoryContext", {})
    advisory_conversation.append({"role": "user", "content": user_message})

    updated_context, coverage, sufficient_context, prepared_summary, follow_up_question = _model_extract_context(
        advisory_conversation, advisory_context, current_objective
    )

    architecture_options = []
    flattened_services = []
    suggested_services = []

    if sufficient_context:
        profile = _context_to_profile(updated_context)
        weights = compute_weights(profile)
        architecture_options = _model_build_options(updated_context, current_objective)

        seen_services = set()
        for block in architecture_options[0]["providers"]:
            for service_info in block["services"]:
                flattened_services.append(f"{get_provider_label(block['provider'])} {service_info['service']}")
                if service_info["service"] not in seen_services:
                    suggested_services.append(service_info["service"])
                    seen_services.add(service_info["service"])

        reply = _model_ready_reply(updated_context, architecture_options[0], current_objective)

        best_option = architecture_options[0]
        best_provider = best_option["providers"][0]["provider"] if len(best_option["providers"]) == 1 else "multi"
        update_session_fields(
            session_id,
            {
                "companyProfile": profile,
                "weights": weights,
                "computedWeights": weights,
                "suggestedServices": suggested_services,
                "provider": best_provider,
                "selectedProvider": best_provider,
                "advisorRecommendations": architecture_options,
            },
        )
    else:
        if not follow_up_question:
            # The model omitted the follow-up — derive one from the missing coverage area
            missing = [area for area, covered in coverage.items() if not covered]
            fallback_map = {
                "business": "Could you tell me a bit about your industry and the type of workload you are running?",
                "scale": "What kind of scale are you expecting — number of users, requests per day, or data volume?",
                "security": "Do you have any compliance requirements such as HIPAA, PCI-DSS, or SOC2?",
                "cost": "How would you describe your budget posture — cost-sensitive, startup budget, or flexible?",
            }
            follow_up_question = fallback_map.get(missing[0] if missing else "business",
                "Could you tell me more about your workload, scale, compliance needs, and budget?")
            logger.warning("Model omitted follow_up_question; using fallback for missing area: %s", missing)
        reply = follow_up_question

    advisory_conversation.append({"role": "assistant", "content": reply})
    reasoning_mode = "bedrock-model"

    # Auto-generate session title from first user message
    if not session_item.get("sessionTitle") and user_message:
        title = user_message.strip()[:60]
        if len(user_message.strip()) > 60:
            title += "..."
        update_session(session_id, "sessionTitle", title)

    conversation_history = session_item.get("conversationHistory", [])
    if not isinstance(conversation_history, list):
        conversation_history = []
    conversation_history.extend(
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": reply},
        ]
    )
    update_session_fields(
        session_id,
        {
            "advisoryConversation": advisory_conversation,
            "advisoryContext": updated_context,
            "advisorReasoningMode": reasoning_mode,
            "advisoryObjective": current_objective,
            "conversationHistory": conversation_history,
        },
    )

    return {
        "sessionId": session_id,
        "reply": reply,
        "sufficient_context": sufficient_context,
        "recommended_services": flattened_services,
        "extracted_fields": updated_context,
        "context_coverage": coverage,
        "architecture_options": architecture_options,
        "prepared_summary": prepared_summary,
        "reasoningMode": reasoning_mode,
        "objective": current_objective,
    }
