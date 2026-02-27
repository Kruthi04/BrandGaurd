"""FastAPI application and route definitions for BrandGuard."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.monitoring import router as monitoring_router
from app.api.analysis import router as analysis_router
from app.api.graph import router as graph_router
from app.api.agent import router as agent_router
from app.api.search import router as search_router
from app.api.investigate import router as investigate_router

app = FastAPI(
    title="BrandGuard API",
    description="Autonomous AI reputation monitoring and brand protection",
    version="0.1.0",
)

# CORS - configure appropriately for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route groups
app.include_router(monitoring_router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
app.include_router(graph_router, prefix="/api/graph", tags=["graph"])
app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(investigate_router, prefix="/api/investigate", tags=["investigate"])


@app.get("/")
async def root():
    return {"service": "BrandGuard API", "version": "0.1.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
