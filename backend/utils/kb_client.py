import logging

import boto3
from botocore.config import Config

from config import settings

logger = logging.getLogger(__name__)

bedrock_agent = boto3.client(
    "bedrock-agent-runtime",
    region_name=settings.AWS_REGION,
    config=Config(connect_timeout=1, read_timeout=2, retries={"max_attempts": 1}),
)


def retrieve_compliance_context(
    query: str,
    frameworks: list[str],
    num_results: int = 5,
) -> str:
    search_query = f"{query} {' '.join(frameworks)}"

    response = bedrock_agent.retrieve(
        knowledgeBaseId=settings.BEDROCK_KB_ID,
        retrievalQuery={"text": search_query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": num_results,
                "overrideSearchType": "HYBRID",
            }
        },
    )

    chunks = []
    for result in response.get("retrievalResults", []):
        content = result.get("content", {}).get("text", "")
        score = result.get("score", 0)
        source = result.get("location", {}).get("s3Location", {}).get("uri", "unknown")
        if score > 0.3:
            chunks.append(f"[Source: {source}]\n{content}")

    return "\n\n---\n\n".join(chunks) if chunks else ""


def get_compliance_context(
    query: str,
    frameworks: list[str],
    num_results: int = 5,
) -> str:
    try:
        if settings.BEDROCK_KB_ID:
            result = retrieve_compliance_context(query, frameworks, num_results)
            if result:
                return result
    except Exception as exc:  # pragma: no cover - depends on AWS
        logger.warning("KB retrieval failed, using fallback: %s", exc)

    from utils.compliance_mapper import get_text

    return get_text(frameworks=frameworks, field_keywords=[])
