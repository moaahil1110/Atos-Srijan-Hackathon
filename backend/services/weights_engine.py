# Pure Python — zero AWS dependencies
# compute_weights(intent: dict) -> {"security": float, "compliance": float, "cost": float}
# All three values always sum to exactly 1.0
# Person 1 owns this file


def compute_weights(intent: dict) -> dict:
    """
    Convert a company profile into priority weights {security, compliance, cost}.
    Deterministic — same input always gives same output.
    All three values always sum to exactly 1.0.
    Security has a hard floor of 0.40 after normalisation.
    """

    # --- Security score ---
    risk_tolerance = intent.get("riskTolerance", 3)
    data_classification = intent.get("dataClassification", "")

    security = 0.40
    security += (5 - risk_tolerance) * 0.04
    if data_classification == "highly-confidential":
        security += 0.08
    security = min(security, 0.70)

    # --- Compliance score ---
    compliance_frameworks = intent.get("complianceFrameworks", [])
    compliance_maturity = intent.get("complianceMaturity", "")

    compliance = 0.00
    # Only score if there are real frameworks (not empty / ["none"])
    has_frameworks = (
        compliance_frameworks
        and compliance_frameworks != ["none"]
        and len(compliance_frameworks) > 0
    )
    if has_frameworks:
        compliance = 0.15
        compliance += 0.05 * (len(compliance_frameworks) - 1)
        if compliance_maturity == "in-progress":
            compliance += 0.10
        elif compliance_maturity == "not-started":
            compliance += 0.05

    # --- Cost score ---
    cost_pressure = intent.get("costPressure", 3)
    cost = (cost_pressure / 5) * 0.25

    # --- Normalise to sum = 1.0 ---
    total = security + compliance + cost
    if total == 0:
        # Fallback: shouldn't happen, but guard against div-by-zero
        return {"security": 1.0, "compliance": 0.0, "cost": 0.0}

    security = round(security / total, 3)
    compliance = round(compliance / total, 3)
    cost = round(cost / total, 3)

    # --- Fix rounding so they sum to exactly 1.0 ---
    rounding_diff = round(1.0 - (security + compliance + cost), 3)
    security = round(security + rounding_diff, 3)

    # --- Final enforcement: security floor = 0.40 ---
    if security < 0.40:
        deficit = round(0.40 - security, 3)
        security = 0.40

        # Subtract deficit from cost first
        if cost >= deficit:
            cost = round(cost - deficit, 3)
        else:
            # Cost can't cover it all — take what we can from cost, rest from compliance
            remaining = round(deficit - cost, 3)
            cost = 0.0
            compliance = round(compliance - remaining, 3)

    return {
        "security": security,
        "compliance": compliance,
        "cost": cost,
    }
