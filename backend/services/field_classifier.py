"""Pure Python — zero AWS dependencies.
classify_field(field, weights, active_frameworks, maturity) -> field with added keys:
  instruction: LOCKED_SECURE | PREFER_SECURE | OPTIMISE_COST | BALANCED
  effectivePriority: float
  complianceActive: bool
"""


def classify_field(field: dict, weights: dict, active_frameworks: list[str],
                   maturity: str = "not-started") -> dict:
    """Tag a schema field with instruction, effectivePriority, complianceActive."""

    sec_rel = field.get("securityRelevance", "none")
    cost_rel = field.get("costRelevance", "none")
    comp_rel = [f.lower() for f in field.get("complianceRelevance", [])]
    active_lower = [f.lower() for f in active_frameworks]

    # ── Check compliance overlap ───────────────────────────────
    compliance_hit = any(f in active_lower for f in comp_rel)

    # ── Compute effective priority ─────────────────────────────
    priority = 0.0

    sec_weight = weights.get("security", 0.40)
    comp_weight = weights.get("compliance", 0.0)
    cost_weight = weights.get("cost", 0.0)

    if sec_rel == "critical":
        priority += sec_weight * 1.0
    elif sec_rel == "high":
        priority += sec_weight * 0.7
    elif sec_rel == "medium":
        priority += sec_weight * 0.4

    if compliance_hit:
        priority += comp_weight * 0.8

    if cost_rel == "high":
        priority += cost_weight * 1.0
    elif cost_rel == "medium":
        priority += cost_weight * 0.5

    # ── Assign instruction tag ─────────────────────────────────
    if sec_rel == "critical":
        instruction = "LOCKED_SECURE"
    elif sec_rel == "high" and sec_weight > 0.50:
        instruction = "PREFER_SECURE"
    elif cost_rel == "high" and cost_weight > 0.15 and sec_rel == "none":
        instruction = "OPTIMISE_COST"
    else:
        instruction = "BALANCED"

    # ── Compliance boost ───────────────────────────────────────
    if compliance_hit:
        if maturity == "in-progress":
            priority *= 1.6
        elif maturity == "not-started":
            priority *= 1.4

    # ── Return enriched field ──────────────────────────────────
    enriched = dict(field)
    enriched["instruction"] = instruction
    enriched["effectivePriority"] = round(priority, 3)
    enriched["complianceActive"] = compliance_hit
    return enriched
