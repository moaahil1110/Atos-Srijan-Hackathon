"""POST /explain — Follow-up questions and counter-asks on fields."""
from fastapi import APIRouter, HTTPException
from models.explain import ExplainRequest
from services.explain_service import explain_field

router = APIRouter()


@router.post("/explain")
async def explain_endpoint(req: ExplainRequest):
    try:
        result = explain_field(
            session_id=req.sessionId,
            field_id=req.fieldId,
            field_label=req.fieldLabel,
            current_value=req.currentValue,
            inline_reason=req.inlineReason,
            message=req.message,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
