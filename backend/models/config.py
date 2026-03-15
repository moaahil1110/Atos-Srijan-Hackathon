# Pydantic models for /config
# ConfigRequest  — { sessionId, schema, service }
# ConfigResponse — { config: { fieldId: { value, reason } } }

from pydantic import BaseModel, Field
from typing import Any


class ConfigRequest(BaseModel):
    sessionId: str
    # Frontend sends "schema" but that's a reserved name in Pydantic v2,
    # so we alias it: JSON key "schema" → Python attr "schema_fields"
    schema_fields: dict[str, Any] | list[dict[str, Any]] = Field(alias="schema")
    service: str

    model_config = {"populate_by_name": True}


class ConfigResponse(BaseModel):
    config: dict[str, Any]
