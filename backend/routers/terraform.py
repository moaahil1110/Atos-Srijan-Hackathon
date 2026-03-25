from fastapi import APIRouter, HTTPException

from models.terraform import TerraformRequest, TerraformResponse
from services.terraform_service import generate_terraform
from utils.dynamo_client import get_configured_services

router = APIRouter()


@router.post("/terraform", response_model=TerraformResponse)
async def terraform_endpoint(req: TerraformRequest):
    try:
        terraform_content = await generate_terraform(req.sessionId, req.service, req.provider)
        services = [req.service] if req.service else get_configured_services(req.sessionId)
        return {
            "terraformContent": terraform_content,
            "service": req.service or "ALL",
            "services": services,
            "sessionId": req.sessionId,
        }
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
