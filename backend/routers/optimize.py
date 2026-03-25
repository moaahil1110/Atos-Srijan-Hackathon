from fastapi import APIRouter, HTTPException

from models.optimize import OptimizeRequest, OptimizeResponse
from services.optimize_service import optimize_config

router = APIRouter()


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_endpoint(req: OptimizeRequest):
    try:
        gaps = await optimize_config(req.sessionId, req.service, req.existingConfig)
        return {"gaps": gaps}
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
