from typing import Any

from pydantic import BaseModel


class OptimizeRequest(BaseModel):
    sessionId: str
    service: str
    existingConfig: dict[str, Any]


class Gap(BaseModel):
    fieldId: str
    currentValue: str
    recommendedValue: str
    severity: str
    reason: str


class OptimizeResponse(BaseModel):
    gaps: list[Gap]
