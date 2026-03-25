from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    sessionId: str | None = None
    message: str


class ChatResponse(BaseModel):
    sessionId: str
    reply: str
    sufficient_context: bool
    recommended_services: list[str]
    extracted_fields: dict[str, str] = {}


class IntentRequest(BaseModel):
    description: str
    provider: str = "aws"


class IntentResponse(BaseModel):
    sessionId: str
    intent: dict[str, Any]
    weights: dict[str, float]
    suggestedServices: list[str]
