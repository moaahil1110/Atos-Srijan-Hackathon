"""Pydantic models for /config endpoint."""
from pydantic import BaseModel
from typing import Optional


class ConfigRequest(BaseModel):
    sessionId: str
    schema_data: dict  # the full schema object from /schema
    service: str


class ConfigResponse(BaseModel):
    config: dict  # { fieldId: { value, reason } }
