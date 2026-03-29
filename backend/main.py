import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routers import config, explain, intent, optimize, schema, sessions, terraform
from utils.local_retrieval import warm_retriever

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


@app.on_event("startup")
async def load_local_indexes():
    warm_retriever()


@app.get("/health")
async def health():
    return {"status": "ok"}


handler = Mangum(app)
