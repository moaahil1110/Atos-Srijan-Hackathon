"""POST /schema — Fetch and classify service schema."""
from fastapi import APIRouter, HTTPException
from models.schema import SchemaRequest
from services.schema_service import fetch_schema

router = APIRouter()


@router.post("/schema")
async def schema_endpoint(req: SchemaRequest):
    try:
        schema = fetch_schema(req.service, req.provider, req.sessionId)
        return {"schema": schema}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
