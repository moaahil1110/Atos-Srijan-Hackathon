from typing import Any

from pydantic import BaseModel, Field


class SchemaRequest(BaseModel):
    sessionId: str
    service: str
    provider: str = "aws"


class SchemaResponse(BaseModel):
    schema_data: dict[str, Any] = Field(alias="schema")
    provider: str
    service: str

    model_config = {"populate_by_name": True}
