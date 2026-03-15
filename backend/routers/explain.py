# POST /explain
# Calls: services/explain_service.py

from fastapi import APIRouter, HTTPException
from models.explain import ExplainRequest, ExplainResponse
from services.explain_service import explain_field

router = APIRouter()


@router.post("/explain", response_model=ExplainResponse)
async def explain_endpoint(req: ExplainRequest):
    try:
        result = await explain_field(
            session_id=req.sessionId,
            field_id=req.fieldId,
            field_label=req.fieldLabel,
            current_value=req.currentValue,
            inline_reason=req.inlineReason,
            message=req.message,
        )
        return result
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
