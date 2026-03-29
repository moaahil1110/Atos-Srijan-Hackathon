import logging

from fastapi import APIRouter, HTTPException, Query

from utils.dynamo_client import get_session, list_user_sessions

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sessions")
async def list_sessions(userId: str = Query(..., description="Firebase UID of the user")):
    """Return all session summaries for a user, newest first."""
    try:
        return list_user_sessions(userId)
    except Exception as exc:
        logger.error("Error listing sessions for user %s: %s", userId, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/sessions/{session_id}")
async def load_session(session_id: str):
    """Return the full session state needed to restore the workspace."""
    try:
        session = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.")
    except Exception as exc:
        logger.error("Error loading session %s: %s", session_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))

    context = session.get("advisoryContext", {})
    coverage = {
        "business": bool(context.get("industry") or context.get("workload_type")),
        "scale": bool(context.get("scale")),
        "security": bool(context.get("compliance") or context.get("security_level")),
        "cost": bool(context.get("budget")),
    }

    service_providers = session.get("serviceProviders", {})
    configured_services = session.get("configuredServices", [])
    service_catalog = {
        svc: {
            "provider": service_providers.get(svc, "aws"),
            "sourceLabel": "Restored session",
        }
        for svc in configured_services
    }

    context_values = [f"{k}: {v}" for k, v in context.items() if v]
    prepared_summary = ", ".join(context_values[:4])

    return {
        "sessionId": session_id,
        "sessionTitle": session.get("sessionTitle", "Previous chat"),
        "chatMessages": session.get("advisoryConversation", []),
        "advisoryContext": context,
        "contextCoverage": coverage,
        "architectureOptions": session.get("advisorRecommendations", []),
        "preparedSummary": prepared_summary,
        "reasoningMode": session.get("advisorReasoningMode", "bedrock-model"),
        "selectedObjective": session.get("advisoryObjective", "recommendation"),
        "allConfigs": session.get("generatedConfig", {}),
        "serviceCatalog": service_catalog,
        "suggestedServices": session.get("suggestedServices", []),
        "currentConfig": session.get("currentConfig", {}),
        "decisionEvidence": session.get("decisionEvidence", {"compliance": [], "provider": []}),
        "createdAt": session.get("createdAt"),
        "updatedAt": session.get("updatedAt"),
    }
