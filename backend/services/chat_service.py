import uuid
import logging
from datetime import datetime, timezone

from utils.bedrock_client import invoke_bedrock_json
from utils.dynamo_client import save_session, get_session, update_session

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """\
You are NIMBUS1000, an expert AI Cloud Architect. Your job is to interview the user about their application to gather enough context to recommend the perfect AWS architecture.

You must ask ONE question at a time to gather missing information. Keep your responses concise, friendly, and professional.

To make an accurate recommendation, you need to understand:
1. The company's industry and workload type.
2. The expected scale (number of users, traffic, data volume) and performance requirements.
3. The estimated cost budget (e.g., in dollars).
4. Any compliance frameworks or high-security needs (e.g., HIPAA, PCI-DSS).

If you DO NOT have enough information across those 4 areas, you must reply with a follow-up question.
If the budget provided is too low for the scale mentioned, you should advise them and suggest compromises, but ultimately you must find a solution that fits their constraints.

Respond ONLY with a valid JSON object matching this exact schema:
{
  "reply": "Your conversational response or follow-up question.",
  "sufficient_context": boolean (true if you have enough info to recommend AWS services, false otherwise),
  "recommended_services": ["S3", "EC2"] (an array of AWS services you recommend. Leave empty if sufficient_context is false. Example services: APIGateway, Lambda, Bedrock, S3, DynamoDB, RDS, EC2, ECS, IAM, Cognito, VPC, CloudFront),
  "extracted_fields": {
    "industry": "string or null — the company's industry if mentioned (e.g. Healthcare, Finance, Retail, SaaS)",
    "workload_type": "string or null — the type of workload (e.g. Web App, Data Pipeline, ML Platform, API Backend)",
    "scale": "string or null — brief summary of expected scale (e.g. '10K daily users', '500GB data', 'High traffic')",
    "budget": "string or null — the stated budget (e.g. '$500/month', '$10K/year', 'Cost-sensitive')",
    "compliance": "string or null — any compliance frameworks mentioned (e.g. 'HIPAA, SOC2', 'PCI-DSS', 'None')",
    "security_level": "string or null — security posture (e.g. 'High — encryption at rest required', 'Standard', 'Enterprise-grade')"
  }
}

IMPORTANT: In extracted_fields, include ONLY fields that the user has explicitly mentioned or confirmed so far. Set fields to null if the user has not yet provided that information. Update fields as the conversation progresses with the latest information.
"""

async def process_chat(session_id: str | None, user_message: str) -> dict:
    if not session_id:
        session_id = str(uuid.uuid4())
        session_item = {
            "sessionId": session_id,
            "conversationHistory": [],
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        save_session(session_item)
    else:
        try:
            session_item = get_session(session_id)
        except KeyError:
            # Recreate if it somehow doesn't exist but an ID was passed
            session_item = {
                "sessionId": session_id,
                "conversationHistory": [],
                "createdAt": datetime.now(timezone.utc).isoformat(),
            }
            save_session(session_item)

    history = session_item.get("conversationHistory", [])
    
    # Append user message
    history.append({"role": "user", "content": [{"text": user_message}]})

    # Call bedrock
    try:
        response_json = invoke_bedrock_json(
            prompt="Respond in JSON format based on the system instructions.",
            system=CHAT_SYSTEM_PROMPT,
            messages=history
        )
    except Exception as e:
        logger.error(f"Error calling Bedrock in chat_service: {e}")
        # pop the user message so we don't save a broken state
        history.pop()
        raise e

    ai_reply = response_json.get("reply", "I encountered an error thinking about that.")
    sufficient_context = response_json.get("sufficient_context", False)
    recommended_services = response_json.get("recommended_services", [])
    extracted_fields = response_json.get("extracted_fields", {})

    # Clean out null values from extracted_fields
    extracted_fields = {k: v for k, v in extracted_fields.items() if v is not None}

    # Append AI response
    history.append({"role": "assistant", "content": [{"text": ai_reply}]})

    # Save updated history
    update_session(session_id, "conversationHistory", history)
    if sufficient_context and recommended_services:
        update_session(session_id, "awsServices", recommended_services)

    return {
        "sessionId": session_id,
        "reply": ai_reply,
        "sufficient_context": sufficient_context,
        "recommended_services": recommended_services,
        "extracted_fields": extracted_fields
    }
