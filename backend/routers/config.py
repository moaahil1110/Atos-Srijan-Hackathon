# POST /config
# Calls: services/config_service.py

from fastapi import APIRouter, HTTPException
from models.config import ConfigRequest, ConfigResponse
from services.config_service import generate_config

router = APIRouter()


@router.post("/config", response_model=ConfigResponse)
async def config_endpoint(req: ConfigRequest):
    try:
        config_map = await generate_config(
            session_id=req.sessionId,
            schema_data=req.schema_fields,
            service=req.service,
        )
        return {"config": config_map}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
