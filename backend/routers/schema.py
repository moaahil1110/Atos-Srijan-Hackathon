# POST /schema
# Calls: services/schema_service.py

from fastapi import APIRouter, HTTPException
from models.schema import SchemaRequest
from services.schema_service import get_schema

router = APIRouter()


@router.post("/schema")
async def schema_endpoint(req: SchemaRequest):
    try:
        result = await get_schema(req.service, req.provider, req.sessionId)
        return {"schema": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
