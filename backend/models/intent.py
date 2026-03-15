# Pydantic models for /intent
# IntentRequest  — { description: str }
# IntentResponse — { sessionId, intent, weights }

from pydantic import BaseModel
from typing import Any


class IntentRequest(BaseModel):
    description: str


class IntentResponse(BaseModel):
    sessionId: str
    intent: dict[str, Any]
    weights: dict[str, float]
