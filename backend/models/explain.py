# Pydantic models for /explain
# ExplainRequest  — { sessionId, fieldId, fieldLabel, currentValue, inlineReason, message }
# ExplainResponse — { response: str, configUpdate: null | { fieldId, newValue, newReason } }

from pydantic import BaseModel
from typing import Any


class ExplainRequest(BaseModel):
    sessionId: str
    fieldId: str
    fieldLabel: str
    currentValue: Any
    inlineReason: str
    message: str


class ConfigUpdate(BaseModel):
    fieldId: str
    newValue: Any
    newReason: str


class ExplainResponse(BaseModel):
    response: str
    configUpdate: ConfigUpdate | None = None
