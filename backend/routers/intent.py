"""POST /intent — Extract company intent from description."""
from fastapi import APIRouter, HTTPException
from models.intent import IntentRequest, IntentResponse
from services.intent_service import extract_intent

router = APIRouter()


@router.post("/intent")
async def intent_endpoint(req: IntentRequest):
    try:
        result = extract_intent(req.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
