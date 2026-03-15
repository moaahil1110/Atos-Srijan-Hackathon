"""main.py — FastAPI entry point
Local dev: uvicorn main:app --reload --port 5000
Lambda:    handler = Mangum(app)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routers import intent, schema, config, explain, terraform

app = FastAPI(
    title="NIMBUS1000 — Cloud Security Copilot",
    description="AI-powered, intent-aware AWS configuration advisor",
    version="1.0.0",
)

# ── CORS — allow all origins for hackathon ─────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────
app.include_router(intent.router, tags=["Intent"])
app.include_router(schema.router, tags=["Schema"])
app.include_router(config.router, tags=["Config"])
app.include_router(explain.router, tags=["Explain"])
app.include_router(terraform.router, tags=["Terraform"])


@app.get("/")
async def root():
    return {
        "service": "NIMBUS1000 Cloud Security Copilot",
        "status": "running",
        "endpoints": ["/intent", "/schema", "/config", "/explain", "/terraform"],
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ── Lambda handler via Mangum ──────────────────────────────────
handler = Mangum(app)
