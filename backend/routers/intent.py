import logging

from fastapi import APIRouter, HTTPException

from models.intent import ChatRequest, ChatResponse, IntentRequest, IntentResponse
from services.chat_service import process_chat
from services.intent_service import extract_intent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        return await process_chat(req.sessionId, req.message, req.objective)
    except Exception as exc:
        logger.error("Error in /chat: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/intent", response_model=IntentResponse)
async def intent_endpoint(req: IntentRequest):
    try:
        return await extract_intent(req.description, req.provider)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error in /intent: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
