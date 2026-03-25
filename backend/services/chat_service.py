import logging
import re
import uuid
from datetime import datetime, timezone

from services.weights_engine import compute_weights
from utils.bedrock_client import invoke_bedrock, invoke_bedrock_json
from utils.dynamo_client import get_session, save_session, update_session
from utils.kb_client import get_compliance_context
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


def _initial_session(session_id: str, objective: str = "recommendation") -> dict:
    normalized_objective = _normalize_objective(objective)
    return {
        "sessionId": session_id,
        "companyProfile": {},
        "computedWeights": {},
        "generatedConfig": {},
        "configuredServices": [],
        "suggestedServices": [],
        "provider": "multi",
        "serviceProviders": {},
        "conversationHistory": {},
        "advisoryConversation": [],
        "advisoryContext": {},
        "advisorRecommendations": [],
        "advisorReasoningMode": "fallback",
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


def _fallback_extract_context(message: str, existing: dict) -> dict:
    text = _normalize_text(message)
    inferred = {}

    if any(token in text for token in ["healthcare", "patient", "clinic", "hospital", "medical"]):
        inferred["industry"] = "healthcare"
    elif any(token in text for token in ["fintech", "bank", "payment", "finance"]):
        inferred["industry"] = "fintech"
    elif any(token in text for token in ["ecommerce", "retail", "store", "marketplace"]):
        inferred["industry"] = "ecommerce"
    elif any(token in text for token in ["saas", "software", "platform", "b2b"]):
        inferred["industry"] = "saas"

    if any(token in text for token in ["api", "backend", "microservice"]):
        inferred["workload_type"] = "api backend"
    elif any(token in text for token in ["analytics", "warehouse", "bigquery", "etl", "data platform"]):
        inferred["workload_type"] = "data platform"
    elif any(token in text for token in ["ai", "ml", "genai", "llm", "inference"]):
        inferred["workload_type"] = "ml platform"
    elif any(token in text for token in ["web app", "portal", "website", "frontend"]):
        inferred["workload_type"] = "web application"

    if any(token in text for token in ["hipaa", "pci", "soc2", "gdpr", "iso27001"]):
        frameworks = []
        for framework in ["HIPAA", "PCI-DSS", "SOC2", "GDPR", "ISO27001"]:
            if framework.lower().replace("-", "") in text.replace("-", ""):
                frameworks.append(framework)
        maturity = ""
        if "in progress" in text or "in-progress" in text:
            maturity = " (in-progress)"
        elif "certified" in text:
            maturity = " (certified)"
        elif "not started" in text or "not-started" in text:
            maturity = " (not-started)"
        inferred["compliance"] = ", ".join(frameworks) + maturity

    if any(token in text for token in ["non-negotiable", "zero trust", "strict security", "sensitive", "regulated"]):
        inferred["security_level"] = "high"
    if any(token in text for token in ["cost sensitive", "tight budget", "budget conscious", "startup budget"]):
        inferred["budget"] = "cost sensitive"

    scale_match = re.search(r"\b\d+[kKmM]?\s+(?:users?|rps|requests?)\b|\b\d+\s*(?:gb|tb|pb)\b", text)
    if scale_match:
        inferred["scale"] = scale_match.group(0)

    stack_hits = [token for token in ["microsoft", "entra", "active directory", "office 365", "windows", "bigquery", "bedrock"] if token in text]
    if stack_hits:
        inferred["current_stack"] = ", ".join(stack_hits)

    return _clean_context(inferred, existing)


def _next_question(context: dict) -> str:
    coverage = _coverage(context)
    prompts = {
        "business": "What are you building, and which industry or customer domain does it serve?",
        "scale": "What scale should I design for, such as users, traffic, or data volume?",
        "security": "Which security or compliance requirements are non-negotiable for this workload?",
        "cost": "What budget or cost sensitivity should I optimize for?",
    }
    for key in ("business", "scale", "security", "cost"):
        if not coverage[key]:
            return prompts[key]
    return "I have enough to recommend an architecture now. Do you want the strongest fit or a couple of alternatives too?"


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
    prompt = f"""
You are Nimbus, a senior multi-cloud architecture advisor conducting discovery.

Current advisory objective:
- {objective_meta['label']}
- {objective_meta['prompt']}
- {objective_meta['follow_up']}

Review the transcript and merge it with the existing context. Return ONLY valid JSON:
{{
  "industry": "string or empty",
  "workload_type": "string or empty",
  "scale": "string or empty",
  "budget": "string or empty",
  "compliance": "string or empty",
  "security_level": "string or empty",
  "current_stack": "string or empty",
  "context_coverage": {{"business": true, "scale": false, "security": true, "cost": false}},
  "sufficient_context": false,
  "prepared_summary": "one or two sentence summary",
  "follow_up_question": "one natural follow-up question if more context is needed, else empty string"
}}

Rules:
- Only include information grounded in the conversation.
- sufficient_context can be true only when business, scale, security, and cost are all known.
- Do not recommend providers or services yet.

Existing context:
{existing_context}

Transcript:
{_conversation_text(conversation)}
""".strip()
    result = invoke_bedrock_json(prompt)
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
    frameworks = _parse_frameworks(context.get("compliance"))
    compliance_text = get_compliance_context(
        f"Best cloud architecture for {context.get('industry', 'regulated')} {context.get('workload_type', 'application')} with {context.get('compliance', 'security controls')}",
        frameworks,
        num_results=5,
    )
    citations = _extract_citations(compliance_text)
    evidence = _extract_evidence(compliance_text)
    allowed_catalog = {
        "aws": get_provider_services("aws"),
        "azure": get_provider_services("azure"),
        "gcp": get_provider_services("gcp"),
    }
    prompt = f"""
You are Nimbus, an expert multi-cloud architecture advisor.

Recommend the best cloud architecture fit for this user. You may return a single-cloud or hybrid option.

Current advisory objective:
- {objective_meta['label']}
- {objective_meta['prompt']}

User requirement trace:
{_matched_requirements(context)}

Compliance documentation:
{compliance_text}

Allowed provider/service catalog:
{allowed_catalog}

Return ONLY valid JSON as an array with up to 3 options:
[
  {{
    "optionId": "short-id",
    "title": "short title",
    "fitScore": 91,
    "summary": "provider-level summary",
    "detailedExplanation": "detailed plain-English explanation tied to user requirements and compliance evidence",
    "tradeoffs": "tradeoff summary",
    "matchedRequirements": ["requirement statements"],
    "providers": [
      {{
        "provider": "aws|azure|gcp",
        "role": "provider role",
        "reason": "why this provider fits",
        "detailedReason": "detailed provider explanation",
        "services": [
          {{
            "service": "provider-specific service name from the allowed catalog",
            "reason": "why this service fits",
            "detailedReason": "detailed service explanation",
            "requirementMatches": ["requirement statements"]
          }}
        ]
      }}
    ]
  }}
]

Rules:
- The top option must be the strongest fit, not the most common cloud.
- You can mix providers if that genuinely matches the requirements best.
- Every provider and service reason must explicitly refer back to the user's requirements.
- Use the compliance documentation to strengthen the explanation. Never invent clause numbers.
- If the objective is Optimise, frame the option as the strongest target state to compare against an existing setup.
- If the objective is Terraform, prefer service combinations that translate cleanly into deployable Terraform and mention implementation readiness in the explanation.
""".strip()
    raw_options = invoke_bedrock_json(prompt)
    if isinstance(raw_options, dict):
        raw_options = raw_options.get("options", [])
    normalized = _normalize_options(raw_options, context, citations, evidence)
    if not normalized:
        raise ValueError("Model returned no valid architecture options.")
    return normalized


def _fallback_options(context: dict) -> list[dict]:
    frameworks = _parse_frameworks(context.get("compliance"))
    compliance_text = get_compliance_context("cloud architecture compliance guidance", frameworks, num_results=4)
    citations = _extract_citations(compliance_text)
    evidence = _extract_evidence(compliance_text)
    providers = ["aws", "azure", "gcp"]
    scores = {"aws": 7, "azure": 7, "gcp": 7}
    text = _normalize_text(" ".join(str(value) for value in context.values()))
    if any(token in text for token in ["microsoft", "entra", "active directory", "office 365", "windows"]):
        scores["azure"] += 4
    if any(token in text for token in ["analytics", "warehouse", "bigquery", "data platform", "ml", "ai"]):
        scores["gcp"] += 4
    if any(token in text for token in ["api", "backend", "serverless", "bedrock", "identity"]):
        scores["aws"] += 4
    ranked = sorted(providers, key=lambda provider: scores[provider], reverse=True)
    concepts = ["identity", "object_storage", "relational_db", "serverless"]

    options = []
    for position, provider in enumerate(ranked[:2], start=1):
        services = []
        for concept in concepts[:3]:
            service_name = get_provider_service_name(concept, provider)
            services.append(
                {
                    "service": service_name,
                    "reason": f"{service_name} fits the workload and control requirements discovered in the conversation.",
                    "detailedReason": f"{service_name} supports the stated workload while keeping the architecture aligned with the user's security, compliance, and cost signals.",
                    "requirementMatches": _matched_requirements(context)[:4],
                    "userRequirementTrace": _matched_requirements(context)[:4],
                    "complianceEvidence": evidence[:2],
                    "citations": citations,
                }
            )
        options.append(
            {
                "optionId": f"{provider}-fallback-{position}",
                "title": f"Best single-cloud fit: {get_provider_label(provider)}",
                "mode": "single-cloud",
                "fitScore": 90 - (position * 6),
                "summary": f"{get_provider_label(provider)} is a strong fallback recommendation based on the discovered workload, security, and stack signals.",
                "detailedExplanation": f"Nimbus selected {get_provider_label(provider)} from the fallback engine because it best matches the user's stated requirements and the retrieved compliance guidance available during reasoning.",
                "tradeoffs": "This fallback option is reliable, but it is less nuanced than the Bedrock-generated architecture analysis.",
                "matchedRequirements": _matched_requirements(context),
                "providers": [
                    {
                        "provider": provider,
                        "role": "Primary cloud",
                        "reason": f"{get_provider_label(provider)} aligns well with the user's current requirements.",
                        "detailedReason": f"The fallback engine matched {get_provider_label(provider)} to the workload pattern, stack signals, and operating constraints described by the user.",
                        "complianceEvidence": evidence[:2],
                        "userRequirementTrace": _matched_requirements(context),
                        "services": services,
                    }
                ],
                "explainability": {
                    "noveltyNote": "Nimbus keeps the architecture explainable by tying every recommendation back to user requirements and compliance evidence, even in fallback mode.",
                    "userRequirementTrace": _matched_requirements(context),
                    "complianceEvidence": evidence,
                    "citations": citations,
                },
            }
        )
    return options


def _model_ready_reply(context: dict, best_option: dict, objective: str) -> str:
    objective_meta = OBJECTIVE_META[_normalize_objective(objective)]
    prompt = f"""
You are Nimbus, a cloud architecture advisor.

Write a concise reply for the user after discovery is complete.
- Tell them you now have enough context for the selected objective.
- Name the strongest recommendation.
- Mention that the providers and services below are explained against their requirements and compliance evidence.
- Mention the current advisory objective: {objective_meta['label']}.
- Keep it to 3 or 4 sentences.

Context:
{context}

Best option:
{best_option}
""".strip()
    return invoke_bedrock(prompt, temperature=0.2, max_tokens=240).strip()


def _reasoning_mode(context_mode: str, option_mode: str | None) -> str:
    if context_mode == "bedrock-model" and option_mode == "bedrock-model":
        return "bedrock-model"
    if context_mode == "fallback" and (option_mode is None or option_mode == "fallback"):
        return "fallback"
    return "hybrid"


async def process_chat(session_id: str | None, user_message: str, objective: str = "recommendation") -> dict:
    current_objective = _normalize_objective(objective)
    if not session_id:
        session_id = str(uuid.uuid4())
        session_item = _initial_session(session_id, current_objective)
        save_session(session_item)
    else:
        try:
            session_item = get_session(session_id)
        except KeyError:
            session_item = _initial_session(session_id, current_objective)
            save_session(session_item)
        else:
            current_objective = _normalize_objective(objective or session_item.get("advisoryObjective"))

    advisory_conversation = session_item.get("advisoryConversation", [])
    advisory_context = session_item.get("advisoryContext", {})
    advisory_conversation.append({"role": "user", "content": user_message})

    try:
        updated_context, coverage, sufficient_context, prepared_summary, follow_up_question = _model_extract_context(
            advisory_conversation, advisory_context, current_objective
        )
        context_mode = "bedrock-model"
    except Exception as exc:
        logger.warning("Model-based advisory extraction unavailable, using fallback extraction: %s", exc)
        updated_context = _fallback_extract_context(user_message, advisory_context)
        coverage = _coverage(updated_context)
        sufficient_context = all(coverage.values())
        prepared_summary = ", ".join(_matched_requirements(updated_context)[:4])
        follow_up_question = _next_question(updated_context)
        context_mode = "fallback"

    architecture_options = []
    flattened_services = []
    suggested_services = []
    option_mode = None

    if sufficient_context:
        profile = _context_to_profile(updated_context)
        weights = compute_weights(profile)
        try:
            architecture_options = _model_build_options(updated_context, current_objective)
            option_mode = "bedrock-model"
        except Exception as exc:
            logger.warning("Model-based architecture recommendation unavailable, using fallback reasoning: %s", exc)
            architecture_options = _fallback_options(updated_context)
            option_mode = "fallback"

        seen_services = set()
        for block in architecture_options[0]["providers"]:
            for service_info in block["services"]:
                flattened_services.append(f"{get_provider_label(block['provider'])} {service_info['service']}")
                if service_info["service"] not in seen_services:
                    suggested_services.append(service_info["service"])
                    seen_services.add(service_info["service"])

        try:
            reply = _model_ready_reply(updated_context, architecture_options[0], current_objective)
        except Exception:
            reply = (
                f"{OBJECTIVE_META[current_objective]['ready']} The strongest fit is {architecture_options[0]['title']}, and I have traced "
                "each provider and service back to your requirements and the compliance evidence used during reasoning."
            )

        best_option = architecture_options[0]
        best_provider = best_option["providers"][0]["provider"] if len(best_option["providers"]) == 1 else "multi"
        update_session(session_id, "companyProfile", profile)
        update_session(session_id, "computedWeights", weights)
        update_session(session_id, "suggestedServices", suggested_services)
        update_session(session_id, "provider", best_provider)
        update_session(session_id, "advisorRecommendations", architecture_options)
    else:
        reply = follow_up_question or _next_question(updated_context)

    advisory_conversation.append({"role": "assistant", "content": reply})
    reasoning_mode = _reasoning_mode(context_mode, option_mode)

    update_session(session_id, "advisoryConversation", advisory_conversation)
    update_session(session_id, "advisoryContext", updated_context)
    update_session(session_id, "advisorReasoningMode", reasoning_mode)
    update_session(session_id, "advisoryObjective", current_objective)

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
