"""Pure Python — zero AWS dependencies.
compute_weights(intent: dict) -> {"security": float, "compliance": float, "cost": float}
All three values always sum to exactly 1.0.
"""


def compute_weights(intent: dict) -> dict:
    """Compute priority weights from the extracted company profile.
    Same input always produces the same output — deterministic, no AI."""

    risk_tolerance = intent.get("riskTolerance", 3)
    cost_pressure = intent.get("costPressure", 3)
    data_classification = intent.get("dataClassification", "")
    frameworks = intent.get("complianceFrameworks", [])
    maturity = intent.get("complianceMaturity", "not-started")

    # ── Security score ─────────────────────────────────────────
    security = 0.40
    security += (5 - risk_tolerance) * 0.04
    if data_classification == "highly-confidential":
        security += 0.08
    security = min(security, 0.70)

    # ── Compliance score ───────────────────────────────────────
    compliance = 0.00
    active = [f for f in frameworks if f.lower() != "none"]
    if active:
        compliance = 0.15
        compliance += max(0, (len(active) - 1)) * 0.05
        if maturity == "in-progress":
            compliance += 0.10
        elif maturity == "not-started":
            compliance += 0.05

    # ── Cost score ─────────────────────────────────────────────
    cost = (cost_pressure / 5) * 0.25

    # ── Normalise to sum = 1.0 ─────────────────────────────────
    total = security + compliance + cost
    if total == 0:
        return {"security": 0.40, "compliance": 0.00, "cost": 0.60}

    security = round(security / total, 3)
    compliance = round(compliance / total, 3)
    cost = round(cost / total, 3)

    # ── Final enforcement: security floor at 0.40 ──────────────
    if security < 0.40:
        deficit = round(0.40 - security, 3)
        security = 0.40
        if cost >= deficit:
            cost = round(cost - deficit, 3)
        else:
            compliance = round(compliance - deficit, 3)

    return {
        "security": security,
        "compliance": compliance,
        "cost": cost,
    }
