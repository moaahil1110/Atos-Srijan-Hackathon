import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routers import config, explain, intent, optimize, schema, sessions, terraform

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = FastAPI(
    title="NIMBUS1000",
    description="GenAI-powered Cloud Security Copilot",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(intent.router)
app.include_router(schema.router)
app.include_router(config.router)
app.include_router(explain.router)
app.include_router(optimize.router)
app.include_router(terraform.router)
app.include_router(sessions.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/test-kb")
async def test_kb():
    from utils.kb_client import get_compliance_context

    result = get_compliance_context(
        query="S3 encryption at rest requirements",
        frameworks=["HIPAA"],
        num_results=3,
    )
    return {
        "length": len(result),
        "preview": result[:500] if result else "EMPTY",
        "using_kb": bool(result and "Source:" in result),
    }


handler = Mangum(app)
