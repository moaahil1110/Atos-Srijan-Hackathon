from fastapi import APIRouter, HTTPException

from models.config import ConfigRequest, ConfigResponse
from services.config_service import generate_config

router = APIRouter()


@router.post("/config", response_model=ConfigResponse)
async def config_endpoint(req: ConfigRequest):
    try:
        return await generate_config(req.sessionId, req.service, req.provider)
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
