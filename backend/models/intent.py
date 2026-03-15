"""Pydantic models for /intent endpoint."""
from pydantic import BaseModel
from typing import Optional


class IntentRequest(BaseModel):
    description: str


class IntentResponse(BaseModel):
    sessionId: str
    intent: dict
    weights: dict
