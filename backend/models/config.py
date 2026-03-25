from typing import Any

from pydantic import BaseModel


class ConfigRequest(BaseModel):
    sessionId: str
    service: str
    provider: str = "aws"


class ConfigResponse(BaseModel):
    config: dict[str, Any]
    service: str
    configuredServices: list[str]
