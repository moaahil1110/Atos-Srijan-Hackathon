"""POST /config — Generate tailored configuration for a service."""
from fastapi import APIRouter, HTTPException, Body
from services.config_service import generate_config

router = APIRouter()


@router.post("/config")
async def config_endpoint(body: dict = Body(...)):
    try:
        session_id = body["sessionId"]
        schema = body.get("schema", body.get("schema_data", {}))
        service = body["service"]
        config = generate_config(session_id, schema, service)
        return {"config": config}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
