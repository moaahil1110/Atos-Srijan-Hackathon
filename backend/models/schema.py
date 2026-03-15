"""Pydantic models for /schema endpoint."""
from pydantic import BaseModel
from typing import Optional


class SchemaRequest(BaseModel):
    service: str
    provider: str = "aws"
    sessionId: str


class SchemaResponse(BaseModel):
    schema_data: dict  # renamed to avoid shadowing Python's schema

    class Config:
        # Allow the response to use "schema" as the JSON key
        populate_by_name = True
