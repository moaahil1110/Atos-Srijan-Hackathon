"""Pydantic models for /explain endpoint."""
from pydantic import BaseModel
from typing import Optional, Any


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
    configUpdate: Optional[ConfigUpdate] = None
