from fastapi import APIRouter, HTTPException

from models.schema import SchemaRequest, SchemaResponse
from services.schema_service import get_schema

router = APIRouter()


@router.post("/schema", response_model=SchemaResponse)
async def schema_endpoint(req: SchemaRequest):
    try:
        schema = await get_schema(req.service, req.provider, req.sessionId)
        return {"schema": schema, "provider": req.provider, "service": req.service}
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
