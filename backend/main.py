# main.py — FastAPI entry point
# Local dev: uvicorn main:app --reload --port 5000
# Lambda:    handler = Mangum(app)

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routers import intent, schema, config, explain, terraform

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# --- FastAPI app ---
app = FastAPI(
    title="NIMBUS1000",
    description="AI-powered AWS cloud configuration advisor",
    version="0.1.0",
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(intent.router)
app.include_router(schema.router)
app.include_router(config.router)
app.include_router(explain.router)
app.include_router(terraform.router)


# --- Health check ---
@app.get("/health")
async def health():
    return {"status": "ok"}


# --- Lambda handler ---
handler = Mangum(app)
