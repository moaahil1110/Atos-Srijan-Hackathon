# POST /intent
# Calls: services/intent_service.py

from fastapi import APIRouter, HTTPException
from models.intent import IntentRequest, IntentResponse
from services.intent_service import extract_intent

router = APIRouter()


@router.post("/intent", response_model=IntentResponse)
async def intent_endpoint(req: IntentRequest):
    try:
        result = await extract_intent(req.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
