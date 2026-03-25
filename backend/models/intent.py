from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    sessionId: str | None = None
    message: str
    objective: str = "recommendation"


class ChatResponse(BaseModel):
    sessionId: str
    reply: str
    sufficient_context: bool
    recommended_services: list[str]
    extracted_fields: dict[str, str] = Field(default_factory=dict)
    context_coverage: dict[str, bool] = Field(default_factory=dict)
    architecture_options: list[dict[str, Any]] = Field(default_factory=list)
    prepared_summary: str = ""
    reasoningMode: str = "fallback"
    objective: str = "recommendation"


class IntentRequest(BaseModel):
    description: str
    provider: str = "aws"


class IntentResponse(BaseModel):
    sessionId: str
    intent: dict[str, Any]
    weights: dict[str, float]
    suggestedServices: list[str]
