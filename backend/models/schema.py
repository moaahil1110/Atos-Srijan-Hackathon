# Pydantic models for /schema
# SchemaRequest  — { service, provider, sessionId }
# SchemaResponse — { schema: { provider, service, fields[] } }

from pydantic import BaseModel
from typing import Any


class SchemaRequest(BaseModel):
    service: str
    provider: str = "aws"
    sessionId: str


class SchemaResponse(BaseModel):
    schema_data: dict[str, Any]  # renamed to avoid shadowing BaseModel.schema

    class Config:
        # Serialise "schema_data" as "schema" in JSON responses
        populate_by_name = True

    def model_dump(self, **kwargs):
        d = super().model_dump(**kwargs)
        if "schema_data" in d:
            d["schema"] = d.pop("schema_data")
        return d
