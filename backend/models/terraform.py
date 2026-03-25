from pydantic import BaseModel


class TerraformRequest(BaseModel):
    sessionId: str
    service: str | None = None
    provider: str = "aws"


class TerraformResponse(BaseModel):
    terraformContent: str
    service: str
    services: list[str]
    sessionId: str
