# Pure Python — zero AWS dependencies
# classify_field(field, weights, active_frameworks, maturity) -> field with added keys:
#   instruction: LOCKED_SECURE | PREFER_SECURE | OPTIMISE_COST | BALANCED
#   effectivePriority: float
#   complianceActive: bool
# Person 1 owns this file


def classify_field(
    field: dict,
    weights: dict,
    active_frameworks: list,
    maturity: str,
) -> dict:
    """
    Take a single field from an AWS service schema, plus the computed weights,
    and return the field augmented with:
      - instruction:        one of LOCKED_SECURE | PREFER_SECURE | OPTIMISE_COST | BALANCED
      - effectivePriority:  float score
      - complianceActive:   bool
    """
    security_relevance = field.get("securityRelevance", "none")
    cost_relevance = field.get("costRelevance", "none")
    compliance_relevance = field.get("complianceRelevance", [])

    # --- Compute effective_priority ---
    effective_priority = 0.0

    # Security component
    sec_multiplier = {"critical": 1.0, "high": 0.7, "medium": 0.4}.get(
        security_relevance, 0.0
    )
    effective_priority += weights.get("security", 0) * sec_multiplier

    # Compliance component — check if field's complianceRelevance overlaps active_frameworks
    compliance_hit = bool(
        set(compliance_relevance) & set(active_frameworks)
    ) if compliance_relevance and active_frameworks else False

    if compliance_hit:
        effective_priority += weights.get("compliance", 0) * 0.8

    # Cost component
    cost_multiplier = {"high": 1.0, "medium": 0.5}.get(cost_relevance, 0.0)
    effective_priority += weights.get("cost", 0) * cost_multiplier

    # --- Assign instruction tag ---
    if security_relevance == "critical":
        instruction = "LOCKED_SECURE"
    elif security_relevance == "high" and weights.get("security", 0) > 0.50:
        instruction = "PREFER_SECURE"
    elif (
        cost_relevance == "high"
        and weights.get("cost", 0) > 0.15
        and security_relevance == "none"
    ):
        instruction = "OPTIMISE_COST"
    else:
        instruction = "BALANCED"

    # --- Compliance boost (after tag assignment) ---
    if compliance_hit:
        if maturity == "in-progress":
            effective_priority *= 1.6
        elif maturity == "not-started":
            effective_priority *= 1.4

    # --- Return augmented field ---
    return {
        **field,
        "instruction": instruction,
        "effectivePriority": round(effective_priority, 4),
        "complianceActive": compliance_hit,
    }
